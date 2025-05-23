import ollama
import re
import json
from .clean import clean_with_regex_and_validate

def _run_ollama(prompt: str, runs: int, model: str, debug: bool = False,) -> list[str]:
    """
    Rejection-sampling wrapper around ollama.chat.
    Keep asking the model until we have `runs` non-empty responses.

    Returns a list of exactly `runs` strings.
    """

    responses: list[str] = []
    attempt = 0

    while len(responses) < runs:
        attempt += 1
        try:
            if debug:
                print(f"[Attempt {attempt}] Gathering response {len(responses)+1}/{runs}", flush=True)

            resp = ollama.chat(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                stream=False
            )
            content = resp["message"]["content"].strip()

            # reject empty or None
            if not content:
                if debug:
                    print(f"  → Empty response, retrying…", flush=True)
                continue

            # accept
            responses.append(content)

        except Exception as e:
            # log the failure, but don't count it
            print(f"Error during attempt {attempt}: {e!r}. Retrying…", flush=True)
            continue

    return responses

def _reprompt_llm(raw_responses: list[str], model: str, debug: bool = False) -> list[str]:
    """
    For each string in raw_responses, keep re-prompting the LLM until we
    successfully extract a JSON list[list[int]]. Returns exactly one
    JSON-formatted string per input.
    """
    reprompted: list[str] = []

    for idx, raw in enumerate(raw_responses, start=1):
        if raw is None:
            raise ValueError(f"raw_responses[{idx}] is None; nothing to reprompt.")

        prompt = (
            "The following response was given by the LLM:\n"
            f"{raw}\n\n"
            "Please extract only the grouping of states as a JSON-formatted list of lists of integers.\n"
            "Do not include markdown, code formatting, or any additional explanation.\n"
            "Return only a JSON list of lists."
        )

        attempt = 0
        while True:
            attempt += 1
            if debug:
                print(f"[Item {idx}] Reprompt attempt {attempt}…", flush=True)

            try:
                resp = ollama.chat(
                    model=model,
                    messages=[{"role": "user", "content": prompt}],
                    stream=False
                )
                content: str = resp["message"]["content"].strip()
            except Exception as e:
                if debug:
                    print(f"  → Error calling model: {e!r} (retrying)", flush=True)
                continue

            # strip markdown fences
            # e.g. ```json\n[...]\n```
            content = re.sub(r"^```(?:json)?\s*", "", content)
            content = re.sub(r"\s*```$", "", content).strip()

            if content == None:
                if debug:
                    print("  → Model returned \"None\"; retrying…")
                continue

            # success!
            reprompted.append(content)
            if debug:
                print(f"  → Success on attempt {attempt}", flush=True)
            break

    return reprompted

def _clean_responses(raw_responses: list[str], model: str, num_states: int) -> list[list[list[int]] | None]:
        reprompted_responses = _reprompt_llm(raw_responses=raw_responses, model=model)
        cleaned_responses = clean_with_regex_and_validate(responses=reprompted_responses, num_states=num_states)
        return cleaned_responses

def query_llm(prompt: str, 
              runs: int, 
              model: str, 
              num_states: int,
              debug: bool = False):
    """
    This is the main function that interacts with the LLM using ollama.
    It sends the prompt to ollama, reprompts it, extracts a grouping and validates that grouping.
    We use rejection sampling in case of errors e.g. communication with the ollama server, badly formatted responses or not being able to extract a grouping.

    Args
    -----
    - `prompt` (str): The prompt in string form that is given to the LLM.
    - `runs` (int): The number of valid prompts and abstractions that we want to receive at the end
    - `model` (str): The name of the model as specified in the ollama library: https://ollama.com/library
    - `num_states` (int): Number of states used for this specific map
    - `debug` (bool): Print out all the debugging information along the way of processing the prompts. Default is False.

    Returns
    -----
    This function returns a dictionary containing `runs` raw responses of the LLMs together with their cleaned, validated abstraction groupings
    
        {
          "raw_responses": [<raw1>, <raw2>, …],

          "cleaned_responses": [<group1>, <group2>, …]
        }
    """
    raw_acc: list[str] = []
    cleaned_acc: list[list[list[int]]] = []
    attempt = 0

    while len(cleaned_acc) < runs:
        need = runs - len(cleaned_acc)
        attempt += 1
        print(f"\n=== Round {attempt}: need {need} more abstractions ===", flush=True)

        # Get `need` non-empty raw replies
        batch_raw = _run_ollama(prompt, need, model, debug)

        # Clean/reprompt them
        batch_cleaned = _clean_responses(batch_raw, model, num_states)

        # Keep only the successful ones, pairing raw->clean
        for raw, grouping in zip(batch_raw, batch_cleaned):
            if grouping is not None:
                raw_acc.append(raw)
                cleaned_acc.append(grouping)
                if debug:
                    print(f"Accepted grouping #{len(cleaned_acc)}", flush=True)
            else:
                if debug:
                    print(f"Rejected raw response (couldn’t clean)", flush=True)

    return {
        "raw_responses": raw_acc[:runs],
        "cleaned_responses": cleaned_acc[:runs],
    }

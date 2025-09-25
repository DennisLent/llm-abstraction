import ollama
import re
import json
from .clean import clean_with_regex_and_validate

def _run_ollama(prompt: str, runs: int, model: str, debug: bool = False) -> list[str]:
    """Collect non-empty responses from an Ollama model.

    Implements rejection sampling around ``ollama.chat`` until exactly
    ``runs`` non-empty responses are obtained.

    Parameters
    ----------
    prompt : str
        User prompt to send to the model.
    runs : int
        Number of valid responses to collect.
    model : str
        Model name as recognized by the Ollama library.
    debug : bool, optional
        If ``True``, print progress messages.

    Returns
    -------
    list of str
        Exactly ``runs`` non-empty model responses.
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
    """Reprompt the model to extract only JSON clusters.

    For each raw response, repeatedly prompt the model to return a
    JSON-formatted ``list[list[int]]`` without any extra text or code
    fences.

    Parameters
    ----------
    raw_responses : list of str
        Raw model responses to post-process.
    model : str
        Model name as recognized by the Ollama library.
    debug : bool, optional
        If ``True``, print progress messages.

    Returns
    -------
    list of str
        One JSON-formatted string per input response.
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
        """Reprompt and validate a batch of responses.

        Parameters
        ----------
        raw_responses : list of str
            Raw model responses.
        model : str
            Model name as recognized by the Ollama library.
        num_states : int
            Total number of ground states used for validation.

        Returns
        -------
        list of list of list of int or None
            Cleaned clusterings for each input, or ``None`` if cleaning failed.
        """
        reprompted_responses = _reprompt_llm(raw_responses=raw_responses, model=model)
        cleaned_responses = clean_with_regex_and_validate(responses=reprompted_responses, num_states=num_states)
        return cleaned_responses

def query_llm(prompt: str, 
              runs: int, 
              model: str, 
              num_states: int,
              debug: bool = False) -> dict:
    """Generate, clean, and validate LLM abstractions.

    Sends a prompt to an Ollama model with rejection sampling, reprompts to
    extract JSON-only clusterings, and validates each clustering.

    Parameters
    ----------
    prompt : str
        The prompt given to the LLM.
    runs : int
        Number of valid abstractions to produce.
    model : str
        Model name as recognized by the Ollama library.
    num_states : int
        Number of ground states in the current map.
    debug : bool, optional
        If ``True``, print progress/debugging information.

    Returns
    -------
    dict
        A dictionary with keys:
        - ``raw_responses``: list of str
        - ``cleaned_responses``: list of list of list of int
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

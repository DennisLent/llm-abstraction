import json
import re

def _extract_grouping(response: str, num_states: int) -> list[list[int]] | None:
    """
    More robust extractor: covers JSON, Python lists, sets, tuples,
    code fences, markdown bullets, Cluster labels, etc.
    """
    valid_states = set(range(num_states))
    resp = response.strip()

    # 1) Remove code fences (```...```)
    resp = re.sub(r"```(?:json)?\s*([\s\S]*?)```", r"\1", resp)

    # 2) Try pure JSON first
    try:
        parsed = json.loads(resp)
        if isinstance(parsed, list):
            # convert any string digits to ints, drop non-ints
            cleaned = []
            for grp in parsed:
                if isinstance(grp, list):
                    nums = []
                    for x in grp:
                        try:
                            # allow "0", "'0'", 0
                            n = int(str(x))
                            if n in valid_states:
                                nums.append(n)
                        except:
                            pass
                    if nums:
                        cleaned.append(nums)
            if cleaned:
                return _validate_and_deduplicate(cleaned, valid_states)
    except:
        pass

    # 3) Normalize all brackets/braces/paren to [ ]
    #    and drop quotes
    norm = resp
    norm = norm.replace("{", "[").replace("}", "]")
    norm = norm.replace("(", "[").replace(")", "]")
    norm = norm.replace("'", "").replace('"', "")

    # 4) Remove labels like "Cluster 1:" or "1:" or "**Cluster 2**:"
    norm = re.sub(r"\*?Cluster\s*\d+\*?\s*[:\-]?", "", norm, flags=re.IGNORECASE)
    norm = re.sub(r"^\s*\d+\s*[:\-]\s*", "", norm, flags=re.MULTILINE)

    # 5) Find all bracketed chunks of text
    chunks = re.findall(r"\[([^\[\]]+)\]", norm)
    clusters = []
    for chunk in chunks:
        # pick up all integers
        nums = [int(x) for x in re.findall(r"\d+", chunk)]
        # only keep clusters with at least one valid state
        nums = [n for n in nums if n in valid_states]
        if nums:
            clusters.append(nums)

    # 6) If we found something, validate & dedupe
    if clusters:
        return _validate_and_deduplicate(clusters, valid_states)

    # 7) Fallback: single lines with "[0]" or "[1,2]" on each line
    lines = norm.splitlines()
    clusters = []
    for L in lines:
        m = re.match(r"\[([^\[\]]+)\]", L.strip())
        if m:
            nums = [int(x) for x in re.findall(r"\d+", m.group(1))]
            nums = [n for n in nums if n in valid_states]
            if nums:
                clusters.append(nums)
    if clusters:
        return _validate_and_deduplicate(clusters, valid_states)

    # Nothing recognized
    return None


def _validate_and_deduplicate(groups: list[list[int]], valid_states: set[int]) -> list[list[int]] | None:
    """
    Deduplicate clusters and ensure all valid_states are covered exactly once.
    """
    deduped = []
    seen = set()
    for grp in groups:
        unique = []
        for s in grp:
            if s in valid_states and s not in seen:
                unique.append(s)
                seen.add(s)
        if unique:
            deduped.append(unique)

    # add any missing states
    missing = valid_states - seen
    if missing:
        deduped.append(sorted(missing))

    return deduped if deduped else None


def clean_with_regex_and_validate(responses, num_states) -> list[list[list[int]] | None]:
    """
    Clean and extract groupings from multiple LLM responses.

    Args:
        responses (list[str]): List of LLM responses.
        num_states (int): Total number of states in the GridWorld.

    Returns:
        list[list[list[int]]] | None: A list of cleaned groupings for each response or None if it was not possible to extract any.
    """
    cleaned_responses = []
    valid_states = set(range(num_states))

    for idx, response in enumerate(responses):
        # print(f"Processing response {idx + 1}/{len(responses)}")
        try:
            cleaned_grouping = _extract_grouping(response, num_states)
            if cleaned_grouping:
                # Validate against valid states
                validated_grouping = _validate_and_deduplicate(cleaned_grouping, valid_states)
                # print(f"Validated grouping for response {idx + 1}: {validated_grouping}")
                cleaned_responses.append(validated_grouping)
            else:
                # print(f"Response {idx + 1} could not be parsed into a valid grouping.")
                cleaned_responses.append(None)
        except Exception as e:
            # print(f"Error processing response {idx + 1}: {str(e)}")
            cleaned_responses.append(None)
    return cleaned_responses

from core_rust import generate_representations_py

def generate_prompts(
    compositions: list[dict],
    prompts: dict[str, list[dict]],
    world: list[list[str]]
) -> list[str]:
    """Compose full prompts from building blocks and a map representation.

    Parameters
    ----------
    compositions : list of dict
        Each composition has keys ``instruction``, ``necessary_context``,
        ``background_contexts`` (list of IDs), ``representation_key``
        (e.g., ``"text"`` or ``"json"``), and ``output``.
    prompts : dict of list of dict
        Prompt fragments keyed by ``instruction``, ``necessary_context``,
        ``context``, and ``output``; each item has ``{"id": ..., "val": ...}``.
    world : list of list of str
        The map used to generate the chosen representation.

    Returns
    -------
    list of str
        Fully rendered prompts in the order of the provided compositions.
    """
    # Build id->val lookup tables for O(1) access and clearer errors
    def build_lookup(items: list[dict]) -> dict[str,str]:
        return {item["id"]: item["val"] for item in items}

    instr_map    = build_lookup(prompts["instruction"])
    necessary_map= build_lookup(prompts["necessary_context"])
    context_map  = build_lookup(prompts["context"])
    output_map   = build_lookup(prompts["output"])

    repr_map = generate_representations_py(world)

    all_prompts = []

    for comp in compositions:
        parts: list[str] = []

        # Instruction (must exist)
        instr_id = comp["instruction"]
        if instr_id not in instr_map:
            raise KeyError(f"Instruction id '{instr_id}' not found in prompt definitions.")
        parts.append(instr_map[instr_id])

        # Necessary context (must exist)
        nc_id = comp["necessary_context"]
        if nc_id not in necessary_map:
            raise KeyError(f"Necessary‐context id '{nc_id}' not found in prompt definitions.")
        parts.append(necessary_map[nc_id])

        # Background contexts (1 or more)
        bg_ids = comp.get("background_contexts", [])
        for bg_id in bg_ids:
            if bg_id not in context_map:
                raise KeyError(f"Background‐context id '{bg_id}' not found in prompt definitions.")
            parts.append(context_map[bg_id])

        # Representation (must exist in repr_map under the chosen key)
        rep_key = comp["representation_key"]
        if rep_key not in repr_map:
            raise KeyError(f"Representation key '{rep_key}' not found; available: {list(repr_map.keys())}")
        parts.append(str(repr_map[rep_key]))

        # Output spec (must exist)
        out_id = comp["output"]
        if out_id not in output_map:
            raise KeyError(f"Output id '{out_id}' not found in prompt definitions.")
        parts.append(output_map[out_id])

        # Join with blank lines between sections
        prompt = "\n".join(parts)
        all_prompts.append(prompt)

    return all_prompts



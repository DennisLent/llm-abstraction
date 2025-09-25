# Prompt Library

- Composition framework: five components — Instruction, Necessary Context, Background Contexts, Representation (`text`/`json`/`adj`), Output.
- Templates live in `config_prompts.yml`; compositions are selected in `config.yml` under `llm.compositions`.
- Variants: prefer JSON representations and explicit output instructions; optional rationale (e.g., `out4`).
- Example (JSON representation):
  - Instruction: role‑style (e.g., `role1`)
  - Necessary: `necessary-domain2`
  - Contexts: e.g., `domain2`, `test3`
  - Representation: `json` from `core_rust.generate_representations_py`
  - Output: `out2` (list[list[int]] only)

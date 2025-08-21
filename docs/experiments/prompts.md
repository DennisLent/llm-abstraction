# Prompts

Prompt compositions pull fragments from `config_prompts.yml` to form instructions, context and expected outputs. The `llm.prompts.generate_prompts` utility assembles these pieces for each map (Thesis).

Fragments include roles (e.g., `role1` – expert in decision‑making), relations (`relation2` – group by spatial behaviour) and outputs (`out1` – list of lists). By varying compositions the experiments test how guidance affects abstraction quality.

Preview all generated prompts with:

```bash
python main.py preview-prompts
```

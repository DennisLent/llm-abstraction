# Models Evaluated

- Families: LLaMA vs Deepseek‑R1; multiple sizes.
- Findings (Thesis): Deepseek‑R1 generally > LLaMA on the composite metric; architecture and prompting strategy matter more than raw size in several cases.
- Practical constraints: local inference via Ollama; hardware budget implies ~70B ceiling.
- Use with CLI: `-m/--model` takes Ollama model names (e.g., `deepseek-r1:7b`, `llama3.1:8b`).

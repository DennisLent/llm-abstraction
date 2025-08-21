# Models

Experiments evaluate different local language models served by [Ollama](https://ollama.com/). Families include LLaMA variants and reasoning‑focused models such as DeepSeek‑R1. Results suggest architecture and instruction tuning matter more than raw parameter count (Thesis).

Switch models by passing their names to CLI commands:

```bash
python main.py benchmark-llm -i 0 -m llama2
```

Multiple models can be provided: `-m llama2 deepseek-r1`. Ensure the models are installed in Ollama and accessible via the same names.

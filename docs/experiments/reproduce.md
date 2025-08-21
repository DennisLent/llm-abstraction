# Reproducing Thesis Results

1. Install dependencies via `./setup.sh`.
2. Use `config.yml` and `config_prompts.yml` as provided.
3. For each model and prompt index run:

```bash
python main.py benchmark-llm -i 0 -m llama2
```

4. After all runs finish, generate ranking tables and plots:

```bash
python main.py analysis
```

Outputs appear under `outputs/` with per‑map folders containing scores and MCTS plots (Thesis).

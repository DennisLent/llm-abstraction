# CLI Reference

The entry point is `main.py`, which exposes several commands via `argparse`.

## preview-prompts

Display generated prompts for all maps.

```bash
python main.py preview-prompts
```

## preview-maps

Render maps and save PNGs under `outputs/maps/`.

```bash
python main.py preview-maps
```

## mcts

Run baseline ground and ideal agents with MCTS.

```bash
python main.py mcts [-d]
```

- `-d, --debug` – show the MCTS tree.

## score-prompts

Generate prompts, query a model and score the resulting clustering.

```bash
python main.py score-prompts -i 0 -m llama2 [-d]
```

- `-i, --index` (required, repeatable) – prompt index from configuration.
- `-m, --model` (required, repeatable) – Ollama model name.
- `-d, --debug` – print intermediate data.

## benchmark-llm

Score prompts and evaluate agents with MCTS.

```bash
python main.py benchmark-llm -i 0 -m llama2 [-g HASH] [-d]
```

- `-g, --maps` – restrict to specific map hashes.

## analysis

Produce plots and ranking tables from previous runs.

```bash
python main.py analysis
```

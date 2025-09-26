# CLI Reference

The command‑line interface in `main.py` organizes all entry points for prompt preview, map rendering, scoring, benchmarking, and analysis. Each subcommand mirrors a function in `llm_abstraction`, so the CLI doubles as documentation for the Python API.

## Commands

### preview‑prompts
Preview the generated prompts for each configured map to verify instruction wording, contexts, and the inserted representation.
- Example: `./env/bin/python main.py preview-prompts`

### preview‑maps
Render maps, compute abstractability labels, and save `map.png` and `abstraction.png` per map to `outputs/maps/`.
- Example: `./env/bin/python main.py preview-maps`

### mcts
Run ground and ideal‑abstraction agents across a grid of simulation budgets and depths. Use the debug flag to print the MCTS tree for inspection.
- Flags: `-d/--debug`
- Example: `./env/bin/python main.py mcts -d`

### score‑prompts
Generate prompts, query the LLM, clean responses, and score clusterings with the bisimulation‑style similarity metric.
- Required: `-i/--index` (one or more prompt indices) and `-m/--model` (one or more Ollama model names)
- Optional: `-d/--debug`
- Example: `./env/bin/python main.py score-prompts -i 0 1 -m deepseek-r1:7b llama3.1:8b`

### benchmark‑llm
Like `score-prompts`, but also run MCTS with the best‑scoring abstraction and write per‑map CSVs and plots.
- Required: `-i/--index`, `-m/--model`
- Optional: `-g/--maps` (one or more map hashes) and `-d/--debug`
- Example: `./env/bin/python main.py benchmark-llm -i 0 -m deepseek-r1:7b -g map_3x3_36a9049c34`

### analysis
Aggregate prior runs into ranking tables, AN(C)OVA outputs, and violin/interaction plots under `outputs/analysis/`.
- Example: `./env/bin/python main.py analysis`

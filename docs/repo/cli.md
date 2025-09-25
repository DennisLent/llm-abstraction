# CLI Reference

- `preview-prompts`
  - Description: Preview generated prompts for each configured map.
  - Args: none
  - Example: `./env/bin/python main.py preview-prompts`

- `preview-maps`
  - Description: Render maps, compute abstractability, and save `map.png`/`abstraction.png` per map.
  - Args: none
  - Example: `./env/bin/python main.py preview-maps`

- `mcts`
  - Description: Run ground vs ideal abstraction agents across simulation budgets/depths.
  - Flags: `-d/--debug` show MCTS tree
  - Example: `./env/bin/python main.py mcts -d`

- `score-prompts`
  - Description: Generate prompts, query the LLM, clean, and score clusterings with the bisimulation similarity metric.
  - Required: `-i/--index` one or more prompt indices; `-m/--model` one or more Ollama model names
  - Optional: `-d/--debug`
  - Example: `./env/bin/python main.py score-prompts -i 0 1 -m deepseek-r1:7b llama3.1:8b`

- `benchmark-llm`
  - Description: Like `score-prompts`, plus run MCTS with the best scoring abstraction.
  - Required: `-i/--index`, `-m/--model`
  - Optional: `-g/--maps` one or more map hashes to restrict evaluation; `-d/--debug`
  - Example: `./env/bin/python main.py benchmark-llm -i 0 -m deepseek-r1:7b -g map_3x3_36a9049c34`

- `analysis`
  - Description: Aggregate results, compute rankings, ANOVA, and generate plots.
  - Args: none
  - Example: `./env/bin/python main.py analysis`

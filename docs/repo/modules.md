# Modules

- Rust core (`src/core`):
  - `game` (e.g., `src/core/game/game_logic.rs`): gridworld dynamics and state encoding.
  - `abstraction/homomorphism.rs`: `get_abstraction`, `get_all_states` for ideal clustering and state enumeration.
  - `utils/matrices.rs`: `build_matrices` to produce `T`,`R`.
  - `runner.rs`: simulation runner used via Python as `PyRunner` (exposed in `src/lib.rs`).
  - `utils/representation.rs`: map representations for prompting.
  - Python bindings in `src/lib.rs`: `PyRunner`, `generate_mdp`, `generate_representations_py`, `visualize_*`, `max_returns`, `min_turns`, `get_number_of_states`.

- Python (`llm_abstraction`):
  - `llm/prompts.py`: `generate_prompts` (assembly from `config_prompts.yml` + `core_rust.generate_representations_py`).
  - `llm/ollama.py`: `query_llm` (wraps `ollama.chat`, reprompts and batches), `_run_ollama`, `_clean_responses`.
  - `llm/clean.py`: `clean_with_regex_and_validate` and `_extract_grouping` for robust parsing.
  - `llm/scoring.py`: `bisimulation_similarity` (Wasserstein + rewards, Hausdorff lifting).
  - `utils/yaml.py`: `load_config`, `parse_maps`.
  - `utils/classify.py`: `classify_abstraction` (reduction thresholding).
  - `evaluation/mcts.py`: `run_mcts`, `run_mcts_llm` and plotting helpers.
  - `evaluation/evaluation_functions.py`: `mcts_evaluation`, `mcts_llm_evaluation` and `map_to_filename` (via `evaluation/saving.py`).
  - `analysis/*`: collection, ANOVA, plotting, ranking (`get_info`, `perform_ANOVA[_z]`, `plot_*`, `rank_*`, `analyze_log_summary`).
  - Package exports at `llm_abstraction/__init__.py` provide lightweight proxies used by `main.py`.

- CLI (`main.py`): subcommands dispatch to `llm_abstraction.*` functions and load `config.yml` / `config_prompts.yml`.

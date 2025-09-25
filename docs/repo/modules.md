# Modules

This section describes the most important modules in the Rust core and the Python layer. For each, we summarize responsibilities and point to the relevant files and public functions in the repository.

Rust core (`src/core`). The gridworld environment, abstraction routines, matrix utilities, runner, and plotting live in the Rust crate.
- `src/core/game/game_logic.rs` encodes the gridworld dynamics and state transitions. It is the basis of the Python‑facing `core_rust` functions that reconstruct a `Game` from a Python list of strings.
- `src/core/abstraction/homomorphism.rs` provides `get_abstraction` and `get_all_states` used to compute ideal clusterings and enumerate reachable states.
- `src/core/utils/matrices.rs` implements `build_matrices` to aggregate transitions and rewards into `T` and `R` matrices used by the scorer.
- `src/core/runner.rs` implements the MCTS runner. In Python, this is exposed as `PyRunner` and supports ground or abstract execution.
- `src/core/utils/representation.rs` produces textual and JSON representations of maps for prompting.
- `src/lib.rs` exposes the Python bindings: `PyRunner`, `generate_mdp`, `generate_representations_py`, `visualize_world_map`, `visualize_abstraction`, `max_returns`, `min_turns`, and `get_number_of_states`.

Python package (`llm_abstraction`). The orchestration code assembles prompts, communicates with the model, cleans responses, scores clusterings, and runs evaluations.
- `llm_abstraction/llm/prompts.py` defines `generate_prompts`, which renders full prompts from `config_prompts.yml` fragments and a world representation supplied by `core_rust`.
- `llm_abstraction/llm/ollama.py` defines `query_llm`, a wrapper around `ollama.chat` with rejection sampling and a reprompting step to extract JSON clusters.
- `llm_abstraction/llm/clean.py` contains `_extract_grouping` and `clean_with_regex_and_validate` to robustly parse and validate model outputs.
- `llm_abstraction/llm/scoring.py` implements `bisimulation_similarity`, which compares a candidate clustering to the ideal using rewards and Wasserstein distances over abstract transitions.
- `llm_abstraction/utils/yaml.py` provides `load_config` and `parse_maps`; `llm_abstraction/utils/classify.py` classifies abstractability by reduction threshold.
- `llm_abstraction/evaluation/mcts.py` provides `run_mcts`/`run_mcts_llm` and plotting helpers; `llm_abstraction/evaluation/evaluation_functions.py` wraps these with `mcts_evaluation`/`mcts_llm_evaluation` and uses `map_to_filename` from `evaluation/saving.py`.
- `llm_abstraction/analysis/*` collects routines for aggregation, AN(C)OVA, and visualization (`get_info`, `perform_ANOVA[_z]`, `plot_*`, `rank_*`, `analyze_log_summary`).
- `llm_abstraction/__init__.py` exposes lightweight proxies so `main.py` can import without heavy side effects.

CLI (`main.py`). The command‑line interface loads `config.yml` and `config_prompts.yml` and dispatches to the functions above. See Repo → CLI Reference for details.

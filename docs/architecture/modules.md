# Modules

## Rust

| Module | Path | Responsibilities | Key items |
|-------|------|-----------------|-----------|
| `game` | `src/core/game` | Grid world definition, `Game` and `State` structs, stateless simulator | `simulate`, `get_state` |
| `abstraction` | `src/core/abstraction` | Compute homomorphisms and build transition/reward matrices | `get_all_states`, `compute_mdp_homomorphism`, `generate_mdp` |
| `runner` | `src/core/runner.rs` | MCTS search over abstract states | `run_mcts`, `search` |
| `simulation` | `src/core/simulation` | Forward model utilities | `simulate_many` |

## Python

| Package | Path | Responsibilities | Public API |
|---------|------|-----------------|-----------|
| `py.llm.prompts` | `py/llm/prompts.py` | Assemble prompts from configuration fragments | `generate_prompts` |
| `py.llm.ollama` | `py/llm/ollama.py` | Query local models via Ollama | `query_llm` |
| `py.llm.clean` | `py/llm/clean.py` | Parse and validate model responses | `clean_with_regex_and_validate` |
| `py.llm.scoring` | `py/llm/scoring.py` | Bisimulation similarity implementation | `bisimulation_similarity` |
| `py.evaluation` | `py/evaluation` | Run baseline and LLM MCTS evaluations | `mcts_evaluation`, `mcts_llm_evaluation` |
| `py.analysis` | `py/analysis` | Post‑processing and plotting of results | `rank_models`, `plot_gain_heatmaps` |


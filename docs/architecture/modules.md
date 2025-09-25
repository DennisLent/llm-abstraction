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
| `llm_abstraction.llm.prompts` | `llm_abstraction/llm/prompts.py` | Assemble prompts from configuration fragments | `generate_prompts` |
| `llm_abstraction.llm.ollama` | `llm_abstraction/llm/ollama.py` | Query local models via Ollama | `query_llm` |
| `llm_abstraction.llm.clean` | `llm_abstraction/llm/clean.py` | Parse and validate model responses | `clean_with_regex_and_validate` |
| `llm_abstraction.llm.scoring` | `llm_abstraction/llm/scoring.py` | Bisimulation similarity implementation | `bisimulation_similarity` |
| `llm_abstraction.evaluation` | `llm_abstraction/evaluation` | Run baseline and LLM MCTS evaluations | `mcts_evaluation`, `mcts_llm_evaluation` |
| `llm_abstraction.analysis` | `llm_abstraction/analysis` | Post‑processing and plotting of results | `rank_models`, `plot_gain_heatmaps` |

# Outputs & Artifacts

Results are written to the `outputs/` directory.

## `outputs/maps/`

Created by `preview-maps`. Each map hash gets its own folder containing:

- `world.png` and `abstraction.png` visualisations.
- `map_abstractability.csv` summarising reduction factor `R` for each map.

## `outputs/llm_scoring/`

Produced by `score-prompts` and `benchmark-llm`. For every map and prompt index the following files are generated:

- `<idx>_<model>_out.json` – extracted clustering.
- `<idx>_<model>_raw_results.csv` – bisimulation scores and MCTS returns.
- `<idx>_<model>_mcts_results.png` – plot of agent performance.

Most commands accept seeds or limits in `config.yml` to make runs reproducible.

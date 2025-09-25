# Outputs & Artifacts

All commands write their artifacts under `outputs/`, organized by purpose and map. This section explains what to expect after running the Quickstart sequence and where to look when reproducing results.

Maps. The `preview-maps` command creates a `maps/` directory and, for each configured world, a folder named `map_<rows>x<cols>_<hash>`. Inside you will find `map.png` and `abstraction.png`, rendered by `core_rust.visualize_world_map` and `core_rust.visualize_abstraction`. The file `map_abstractability.csv` summarizes each map’s abstractability label computed by `llm_abstraction.utils.classify.classify_abstraction`.

LLM scoring and benchmarking. The `score-prompts` and `benchmark-llm` commands write to `llm_scoring/`. For every map, the best‑scoring abstraction and supporting data are saved under the map’s folder. The file `<promptIndex>_<model>_out.json` records the raw and cleaned responses and their similarity scores. If you run MCTS via `benchmark-llm`, two additional files appear: `<promptIndex>_<model>_raw_results.csv` contains agent returns per budget and depth, and `<promptIndex>_<model>_mcts_results.png` plots those curves along with the optimal‑return baseline from `core_rust.max_returns`. A `log_summary.csv` at the root aggregates high‑level run information.

Analysis. The `analysis` command merges model‑based and planning metrics into ranking tables and produces a series of plots (violin, interaction, and gain curves) under `outputs/analysis/`. It also writes AN(C)OVA summaries and Tukey HSD comparisons as CSVs to support statistical inspection.

Determinism. To improve reproducibility, keep simulation limits, depths, and the discount `gamma` fixed and, where possible, set random seeds in runners. The combination of saved prompts, JSON clusterings, and CSV results should let you retrace and verify any figure from the Thesis.

# Outputs & Artifacts

- Root: `outputs/`
  - `maps/`
    - `map_abstractability.csv`: per-map label from `utils/classify.classify_abstraction`.
    - `map_<rows>x<cols>_<hash>/map.png`, `abstraction.png`: rendered via `core_rust.visualize_*`.
  - `llm_scoring/`
    - `<map_hash>/<promptIndex>_<model>_out.json`: raw/cleaned responses and scores per map.
    - `<map_hash>/<promptIndex>_<model>_raw_results.csv`: MCTS results per agent/depth/limit.
    - `<map_hash>/<promptIndex>_<model>_mcts_results.png`: plots with optimal‑return baseline.
    - `log_summary.csv`: aggregated logs.
  - `analysis/`
    - `ranking.csv`, `total_model_ranking.csv`, `total_model_prompt_ranking.csv`.
    - AN(C)OVA summaries and Tukey HSD CSVs.
    - `violin_*.png`, `interaction_*.png`, `representation_performance.png`, `avg_score_by_family_size.png`, etc.

- Determinism knobs: seeds (runner), simulation limits/depths, discount `gamma`.

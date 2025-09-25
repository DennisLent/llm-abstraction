# Reproducing the Thesis

- Environment
  - Ensure Rust toolchain (nightly) and Python env via `./setup.sh`.
- Maps & metadata
  - `./env/bin/python main.py preview-maps`
  - Artifacts in `outputs/maps/`; `map_abstractability.csv` is appended with new maps.
- LLM abstraction + planning
  - Choose prompt index and model(s); for example:
    - `./env/bin/python main.py benchmark-llm -i 0 -m deepseek-r1:7b -g map_3x3_36a9049c34`
  - For full sweeps, iterate over indices/models as in the thesis setting.
- Analysis
  - `./env/bin/python main.py analysis`
  - Tables/plots in `outputs/analysis/` match the thesis figure set.
- Notes
  - Raw per-map JSON and CSV/PNGs for MCTS land in `outputs/llm_scoring/<map_hash>/`.
  - See Repo → CLI Reference for flags and exact outputs.

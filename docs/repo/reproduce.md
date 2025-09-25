# Reproducing the Thesis

This section describes how to recreate the main tables and plots from the Thesis using the provided CLI. The workflow matches the experimental pipeline and writes all artifacts to `outputs/` for inspection.

Environment. Install the nightly Rust toolchain and set up the Python environment with `./setup.sh`. This compiles the Rust extension and installs all Python dependencies used in the orchestration and analysis steps.

Maps and metadata. Start by rendering maps and computing abstractability labels:

```bash
./env/bin/python main.py preview-maps
```

This command writes one folder per map under `outputs/maps/` and appends entries to `outputs/maps/map_abstractability.csv` when new maps are encountered.

LLM abstraction and planning. Choose one or more prompt indices and model names and run benchmarking. To target a specific map hash, pass it with `-g`:

```bash
./env/bin/python main.py benchmark-llm -i 0 -m deepseek-r1:7b -g map_3x3_36a9049c34
```

The command writes JSON responses, MCTS logs, and plots under `outputs/llm_scoring/<map_hash>/` using filenames that include the prompt index and model.

Analysis. Aggregate results across maps and configurations and produce figures and rankings:

```bash
./env/bin/python main.py analysis
```

The outputs in `outputs/analysis/` mirror the figures and tables discussed in the Thesis. For finer control over which maps and models are evaluated, see Repo → CLI Reference for the relevant flags.

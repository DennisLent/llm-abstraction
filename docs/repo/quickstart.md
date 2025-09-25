# Quickstart

This page shows how to set up the project locally and run a complete pass from map preview to analysis. The steps below assume a Linux environment; the CI uses Python 3.11/3.12 and a nightly Rust toolchain.

Prerequisites. Install a recent Python (3.10+) and the Rust toolchain with `rustup` on nightly. On Ubuntu, you may also need system libraries for font rendering, as shown in the CI workflows.

Install. From the repository root, run `./setup.sh` to create a virtual environment, build the Rust extension, and install Python dependencies. The script places the virtualenv under `./env/`.

Minimal demo. With the environment set up, the following commands exercise the main functionality:

```bash
./env/bin/python main.py preview-maps
./env/bin/python main.py mcts
./env/bin/python main.py score-prompts -i 0 -m llama3.1:8b
./env/bin/python main.py benchmark-llm -i 0 -m deepseek-r1:7b
./env/bin/python main.py analysis
```

Outputs. All artifacts are written to `outputs/`. Map previews create per‑map folders with `map.png` and `abstraction.png`. Scoring and benchmarking write JSON clusterings, CSV logs, and MCTS plots to `outputs/llm_scoring/`. The analysis step aggregates results under `outputs/analysis/`. See Repo → Outputs & Artifacts for details.

Configuration. Experiment settings live in `config.yml`, and prompt fragments live in `config_prompts.yml`. See Repo → Configuration for the schema and examples.

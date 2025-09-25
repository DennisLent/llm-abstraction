# Quickstart

- Prerequisites: Python 3.10+ (CI uses 3.11/3.12), Rust toolchain (nightly), Linux tested on Ubuntu 24.04.
- Install: run `./setup.sh` to set up the virtualenv and build the Rust extension.
- Minimal demo commands:
  - `./env/bin/python main.py preview-maps`
  - `./env/bin/python main.py mcts`
  - `./env/bin/python main.py score-prompts -i 0 -m llama3.1:8b`
  - `./env/bin/python main.py benchmark-llm -i 0 -m deepseek-r1:7b`
  - `./env/bin/python main.py analysis`
- Outputs land under `outputs/` (see Repo → Outputs & Artifacts).
- Configuration lives in `config.yml` and `config_prompts.yml` (see Repo → Configuration).

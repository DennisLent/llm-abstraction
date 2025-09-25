# LLM-Based State Abstraction

[![Docs](https://img.shields.io/badge/docs-mkdocs--material-blue)](https://dennislent.github.io/llm-abstraction/)
[![codecov](https://codecov.io/gh/DennisLent/llm-abstraction/branch/main/graph/badge.svg)](https://codecov.io/gh/DennisLent/llm-abstraction)

This repository contains the code for a thesis exploring how large language models can derive state abstractions for a simple grid‑world game. Heavy computation runs in Rust for performance and memory safety, while Python orchestrates configuration, LLM calls and evaluation.

For full docs please visit: [dennislent.github.io/llm-abstraction](https://dennislent.github.io/llm-abstraction/)

## Project layout

```
├── src/                # Rust crate with core game logic and utilities
├── py/                 # Python package wrapping the Rust library and analysis helpers
├── main.py             # Command line entry point for experiments
├── container/          # Apptainer/Singularity definition used in CI and HPC environments
└── tests/              # Python and Rust tests
```

## Requirements

- Python 3.10+
- rustup (Nightly toolchain)
- Linux (tested on Ubuntu 24.04 LTS & Manjaro 6.12)

Install all dependencies and build the Rust extension with:

```bash
./setup.sh
```

## Usage

Configuration lives in `config.yml` and `config_prompts.yml`. The CLI exposes several commands:

```bash
python main.py preview-prompts                      # print generated prompts
python main.py preview-maps                         # save map PNGs and metadata to outputs/
python main.py mcts                                 # run baseline MCTS agents
python main.py score-prompts -i 0 -m llama2         # score abstractions for a model
python main.py benchmark-llm -i 0 -m llama2         # run MCTS with LLM abstraction
python main.py analysis                             # produce plots and ranking tables
```

Results are written to the `outputs/` directory.

### Configuration files

- **config.yml** – specifies grid maps, simulation settings under `mcts_variables`, and which prompt compositions to use via `llm`.
- **config_prompts.yml** – defines reusable prompt fragments referenced by `config.yml`.

The utilities read these files to decide which maps to process, how prompts are assembled and how evaluations run.

### Linting

Python style is enforced with `flake8`. The list of ignored rules and their justification is documented in [`docs/flake8-ignores.md`](docs/flake8-ignores.md).

### Rust core library

The `rust_core` Python module exposes the Rust computation routines:

- `PyRunner` – run simulations and MCTS from Python
- `max_returns` and `min_turns` – compute theoretical bounds for a world
- `visualize_world_map` and `visualize_abstraction` – render grids and abstractions as PNGs
- `generate_representations_py` – produce JSON, text and adjacency list representations
- `generate_mdp` – build transition and reward matrices with cluster labels

### Testing

Run the full test suite (Rust and Python):

```bash
cargo test
pytest
```

Continuous integration additionally runs a small end‑to‑end check that executes the CLI on sample data to ensure the Python and Rust components integrate correctly.

## License

This project is released under the MIT license.

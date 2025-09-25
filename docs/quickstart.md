# Quickstart

Follow these steps to run the prototype in minutes.

## Prerequisites

- Linux (tested on Ubuntu 24.04)
- Python 3.10+
- `rustup` with a nightly toolchain

## Installation

Clone the repository and install dependencies:

```bash
./setup.sh
```

This script installs Python packages from `requirements.txt` and builds the Rust extension.

## Run a demo

Generate map images and metadata:

```bash
python main.py preview-maps
```

Score an abstraction for the first prompt using a local model name:

```bash
python main.py score-prompts -i 0 -m llama2
```

For a full benchmark that scores and evaluates with MCTS:

```bash
python main.py benchmark-llm -i 0 -m llama2
```

Outputs are written to `outputs/`.

## Reproducibility and Compute

For reproducibility on shared infrastructure, it is recommended to run the project inside a container on a compute cluster. The repository includes definitions under `container/` suitable for Apptainer/Singularity. Running inside a container isolates system dependencies and helps obtain consistent results across machines.

Benchmarks can be compute‑intensive due to repeated rollouts and model queries. To conserve resources, run a single benchmark at a time (for a specific prompt index and model) rather than sweeping many configurations in one session.

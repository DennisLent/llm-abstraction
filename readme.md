# Thesis Prototype v4

This thesis explores using large language models to derive state abstractions for a simple grid-world game. The heavy computation is implemented in Rust for performance and memory safety while Python orchestrates configuration, LLM calls and evaluation.

The repository is organised as follows:

- `src/` – Rust crate providing the core game logic and abstraction utilities.
- `py/` – Python package that wraps the Rust library and adds analysis and evaluation helpers.
- `main.py` – command line entry point for running experiments.
- `container/container.def` – definition for the container image used in CI and on
  high‑performance computing clusters.

## Requirements

The setup has only been tested on Ubuntu 24.04 LTS. In order to run this prototype you will need:

- Python 3.10+
- rustup

Before running any code, please ensure to run the setup script to install dependencies and build the Rust library:

```
./setup.sh
```

## Usage

All configuration lives in `config.yml` and `config_prompts.yml`. The project
exposes several commands through `main.py`:

```
python main.py preview-prompts       # print generated prompts
python main.py preview-maps          # save map PNGs and metadata to outputs/
python main.py mcts                  # run baseline MCTS agents
python main.py score-prompts -i 0 -m llama2       # score abstractions for a model
python main.py benchmark-llm -i 0 -m llama2       # run MCTS with LLM abstraction
python main.py analysis              # produce plots and ranking tables
```

Results are written to the `outputs/` directory.

### Configuration files

- `config.yml` – specifies the grid maps under `game`, simulation settings
  under `mcts_variables`, and which prompt compositions to use via `llm`.
- `config_prompts.yml` – defines reusable prompt fragments referenced by the
  `compositions` entries in `config.yml`.

The CLI utilities read these files to decide which maps to process, how prompts
are assembled and how evaluations are run.

### Linting

Python style is enforced with flake8. The list of disabled rules and their
justification is documented in [`docs/flake8-ignores.md`](docs/flake8-ignores.md).

### The `rust_core` Library

The `core_rust` extension module exposes the Rust computation routines to Python. It provides one main class and several helper functions:

#### Class: `PyRunner`

A wrapper around the Rust Runner that allows running simulations and MCTS in Rust from Python.

- `__init__(py_world: List[List[str]], abstracted: bool, py_abstraction: Optional[List[List[int]]])`: Constructor for the runner
- `run(sim_limit: int, sim_depth: int, c: float, gamma: float, seed: Optional[int], max_turns: int, runs: int, debug: bool, show_mcts: bool) -> List[Tuple[int, float]]`: Runs the MCTS agent with the given configurations and returns the number of turns and score of each run.

#### Functions

- `max_returns(py_world: List[List[str]], gamma: float) -> float`: Computes the maximum possible discounted return for a given world by finding the minimum number of turns to finish and applying the discount factor.
- `min_turns(py_world: List[List[str]]) -> int`: Returns the minimum number of turns required to complete the game in the given world.
- `visualize_world_map(py_world: List[List[str]], output_dir: str) -> None`: Draws the world grid as a PNG (map.png) in `output_dir`. The map is scaled to 500×500 pixels.
- `visualize_abstraction(py_world: List[List[str]], output_dir: str) -> None`: Computes state abstraction clusters and draws them over the world grid as abstraction.png in `output_dir`.
- `generate_representations_py(py_world: List[List[str]]) -> Dict[str, Any]`: Generates JSON representations, plain-text description, and adjacency list for the game graph. Returns a Python dict with keys: `json`, `text` and `adj`.
- `generate_mdp(py_world: List[List[str]]) -> Dict[str, Any]`: Builds the transition (T) and reward (R) matrices for the MDP abstraction, along with cluster labels. Returns a Python dict with: `T`, `R` and `abstraction`.

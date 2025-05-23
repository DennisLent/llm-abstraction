# Thesis Prototype v4

This prototype of the thesis outsources all the computation to Rust. In rust, we run the game and the agents, which not only improves speed, but we can ensure that the operations are run memory safe, to not create memory leaks like in C / C++. The rust_core is then exposed to Python and can be called from it. Most of the code is still written in Python, as Ollama and it's Python API is used for LLM calls and it is realitively easy to use.

## Requirements

The setup has only been tested on Ubuntu 24.04 LTS. In order to run this prototype you will need:

- Python 3.10 >
- rustup

Before running any code, please ensure to run the setup script to ensure that all dependencies are installed and the rust libraries are compiled.

`./setup.sh`

## Usage

The main way to configure and run the project is through the config.yml file. The file includes sections for the game configuration, agent configuration and prompt generation. All results are then saved to the outputs folder.

### The `rust_core` Library

The core_rust extension module exposes the Rust computation routines to Python. It provides one main class and several helper functions:

#### Class: `PyRunner`

A wrapper around the Rust Runner that allows running simulations and MCTS in Rust from Python.

- `__init__(py_world: List[List[str]], abstracted: bool, py_abstraction: Optional[List[List[int]]])`: Constructor for the runner
- `run(sim_limit: int, sim_depth: int, c: float, gamma: float, seed: Optional[int], max_turns: int, runs: int, debug: bool, show_mcts: bool) -> List[Tuple[int, float]]`: Runs the MCTS agent with the given configurations and returns the number of turns and score of each run.

#### Functions

- `max_returns(py_world: List[List[str]], gamma: float) -> float`: Computes the maximum possible discounted return for a given world by finding the minimum number of turns to finish and applying the discount factor.
- `min_turns(py_world: List[List[str]]) -> int`: Returns the minimum number of turns required to complete the game in the given world.
- `visualize_world_map(py_world: List[List[str]], output_dir: str) -> None`: Draws the world grid as a PNG (map.png) in output_dir. The map is scaled to 500×500 pixels.
- `visualize_abstraction(py_world: List[List[str]], output_dir: str) -> None`: Computes state abstraction clusters and draws them over the world grid as abstraction.png in output_dir.
- `generate_representations_py(py_world: List[List[str]]) -> Dict[str, Any]`: Generates JSON representations, plain-text description, and adjacency list for the game graph. Returns a Python dict with keys: `json`, `text` and `adj`.
- `generate_mdp(py_world: List[List[str]]) -> Dict[str, Any]`: Builds the transition (T) and reward (R) matrices for the MDP abstraction, along with cluster labels. Returns a Python dict with: `T`, `R` and `abstraction`

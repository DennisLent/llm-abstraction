# Rust API

The Rust crate in `src/` implements the grid‑world and homomorphism logic. Python calls into it through `pyo3` bindings.

## Core modules

- `core/game/game_logic.rs` – defines the `Game` struct, movement rules and reset logic.
- `core/abstraction/homomorphism.rs` – BFS over reachable states (`get_all_states`) and partition refinement (`compute_mdp_homomorphism`).

## Python bindings

| Function | Description | Source |
|----------|-------------|--------|
| `PyRunner::run(sim_limit, sim_depth, c, gamma, seed, max_turns, runs, debug, show_mcts)` | Execute MCTS on ground or abstract states. | `src/lib.rs` |
| `generate_mdp(world)` | Return transition matrix `T`, reward matrix `R`, and the optimal abstraction. | `src/lib.rs` |
| `generate_representations_py(world)` | Produce text/JSON/adjacency representations for prompts. | `src/lib.rs` |
| `visualize_world_map(world, output_dir)` | Save a PNG of the grid world. | `src/lib.rs` |
| `visualize_abstraction(world, output_dir)` | Draw state clusters derived from `compute_mdp_homomorphism`. | `src/lib.rs` |
| `min_turns(world)` / `max_returns(world, gamma)` / `get_number_of_states(world)` | Utility helpers for analyses. | `src/lib.rs` |

These functions are exported through the `core_rust` module and power the Python CLI.

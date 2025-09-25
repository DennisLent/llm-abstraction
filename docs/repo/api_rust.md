# API (Rust → Python bindings)

The `core_rust` module exposes the Rust core to Python via `pyo3`. It lets Python construct worlds, run MCTS episodes, draw artifacts, and assemble matrices required for scoring. The bindings are implemented in `src/lib.rs` and wrap types and functions from `src/core/*`.

Key bindings. Create a `PyRunner` by passing a world grid, a boolean indicating abstract or ground execution, and an optional explicit abstraction (clusters). Call `run` with simulation parameters to produce per‑episode returns. Utility functions compute the maximum possible discounted return (`max_returns`) and the minimum number of turns to reach the goal (`min_turns`). Plotting helpers render `map.png` and `abstraction.png`. Finally, `generate_representations_py` returns JSON and text encodings of the map, and `generate_mdp` returns `T`, `R`, and the ideal `abstraction`. Use `get_number_of_states` to validate response coverage.

Internals. These bindings delegate to the Rust `Game` implementation (`core::game::game_logic::Game`), the abstraction routines (`core::abstraction::homomorphism::get_abstraction`), the matrix builder (`core::utils::matrices::build_matrices`), and the MCTS runner (`core::runner::Runner`).

# API (Rust → Python bindings)

- Module name: `core_rust` (from `src/lib.rs`).
- Public functions:
  - `PyRunner(py_world, abstracted, py_abstraction=None)`: create a runner (wraps `core::runner::Runner`).
  - `PyRunner.run(sim_limit, sim_depth, c, gamma, seed, max_turns, runs, debug, show_mcts)` → list of `(turns, return, (visits, unique))` per episode.
  - `max_returns(py_world, gamma)` → optimal discounted return given the map and discount.
  - `min_turns(py_world)` → minimum steps to goal.
  - `visualize_world_map(py_world, output_dir)` → writes `map.png`.
  - `visualize_abstraction(py_world, output_dir)` → writes `abstraction.png`.
  - `generate_representations_py(py_world)` → `{json, text, adj}` strings.
  - `generate_mdp(py_world)` → `{T, R, abstraction}`.
  - `get_number_of_states(py_world)` → `usize`.
- Internals map to:
  - `core::game::game_logic::Game`
  - `core::abstraction::homomorphism::get_abstraction`
  - `core::utils::matrices::build_matrices`
  - `core::runner::Runner`

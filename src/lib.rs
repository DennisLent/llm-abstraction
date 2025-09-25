//! Python bindings for the core GridWorld + MCTS abstraction crate.
//!
//! This crate exposes a minimal, typed interface to Python via pyo3. It allows
//! you to:
//! - Compute optimal discounted returns and shortest paths for a world.
//! - Visualize worlds and learned abstractions.
//! - Run MCTS either in the ground MDP or in an abstracted MDP.
//! - Build transition/reward matrices and enumerate state counts.
//!
//! The Rust types and modules remain available for native Rust use under
//! `crate::core`. The Python module installs under the name `core_rust`.
#![allow(clippy::too_many_arguments, clippy::type_complexity, deprecated)]

use ordered_float::Pow;
use pyo3::exceptions::{PyRuntimeError, PyValueError};
use pyo3::prelude::*;
use pyo3::types::PyDict;
pub mod core;
use crate::core::abstraction::homomorphism::get_abstraction;
use crate::core::game::game_logic::Game;
use crate::core::runner::Runner;
use crate::core::utils::min_turns::min_turns_to_finish;
use crate::core::utils::plotting::{draw_abstraction, draw_world};
use core::abstraction::homomorphism::get_all_states;
use core::game::utils::actions::Action;
use core::utils::matrices::build_matrices;
use core::utils::representation::generate_representations;
use std::path::Path;

/// Convert a Python ``list[list[str]]`` map into a Rust grid of chars.
fn py_to_world(py_world: Vec<Vec<String>>) -> PyResult<Vec<Vec<char>>> {
    py_world
        .into_iter()
        .map(|row| {
            row.into_iter()
                .map(|s| {
                    // if you want to allow only single-character strings:
                    let mut chars = s.chars();
                    if let (Some(ch), None) = (chars.next(), chars.next()) {
                        Ok(ch)
                    } else {
                        Err(PyValueError::new_err(
                            "Each string must be exactly one character",
                        ))
                    }
                })
                .collect()
        })
        .collect()
}

/// Python wrapper for the Rust `Runner`, capable of executing MCTS episodes.
#[pyclass]
pub struct PyRunner {
    inner: Runner,
}

#[pymethods]
impl PyRunner {
    #[new]
    /// Create a new `PyRunner`.
    ///
    /// Parameters
    /// ----------
    /// py_world
    ///     2D map of single-character strings.
    /// abstracted
    ///     If true, run in the abstract MDP; otherwise run in the ground MDP.
    /// py_abstraction
    ///     Optional custom abstraction (clusters of ground-state IDs).
    pub fn new(
        py_world: Vec<Vec<String>>,
        abstracted: bool,
        py_abstraction: Option<Vec<Vec<isize>>>,
    ) -> PyResult<Self> {
        let world = py_to_world(py_world)?;
        let game = Game::new(world).map_err(|e| PyRuntimeError::new_err(format!("{:?}", e)))?;
        let runner = Runner::new(&game, abstracted, py_abstraction);
        Ok(PyRunner { inner: runner })
    }

    /// Run `runs` episodes of MCTS and return per-episode results.
    pub fn run(
        &mut self,
        sim_limit: i32,
        sim_depth: i32,
        c: f32,
        gamma: f32,
        seed: Option<u64>,
        max_turns: i32,
        runs: usize,
        debug: bool,
        show_mcts: bool,
    ) -> PyResult<Vec<(i32, f32, (usize, usize))>> {
        Ok(self.inner.run(
            sim_limit, sim_depth, c, gamma, seed, max_turns, runs, debug, show_mcts,
        ))
    }
}

/// Compute the maximum achievable discounted return from the initial state.
#[pyfunction]
fn max_returns(py_world: Vec<Vec<String>>, gamma: f32) -> PyResult<f32> {
    let world = py_to_world(py_world)?;
    let game = Game::new(world).map_err(|e| PyRuntimeError::new_err(format!("{:?}", e)))?;

    let min_turns =
        min_turns_to_finish(&game).map_err(|e| PyRuntimeError::new_err(format!("{:?}", e)))? as i32;

    let max_returns = gamma.pow(min_turns);

    Ok(max_returns)
}

/// Compute the minimum number of turns to reach the goal.
#[pyfunction]
fn min_turns(py_world: Vec<Vec<String>>) -> PyResult<usize> {
    let world = py_to_world(py_world)?;
    let game = Game::new(world).map_err(|e| PyRuntimeError::new_err(format!("{:?}", e)))?;
    let min_turns =
        min_turns_to_finish(&game).map_err(|e| PyRuntimeError::new_err(format!("{:?}", e)))?;

    Ok(min_turns)
}

/// Save a rasterized visualization of the map to ``<output_dir>/map.png``.
#[pyfunction]
fn visualize_world_map(py_world: Vec<Vec<String>>, output_dir: &str) -> PyResult<()> {
    let world = py_to_world(py_world)?;
    let world_size = world.len() as u32;

    // Render a 500×500 map, computing cell size from dimensions
    let cell_size = 500 / world_size;

    let dir = Path::new(output_dir);
    let out_file = dir.join("map.png");
    let out_path_str = out_file
        .to_str()
        .ok_or_else(|| PyRuntimeError::new_err("Invalid output path"))?;

    draw_world(&world, out_path_str, cell_size)
        .map_err(|_| PyRuntimeError::new_err("Plotting error"))?;
    println!("Saved world visualization to: {:?}", out_path_str);

    Ok(())
}

/// Save a rasterized visualization of the learned abstraction to
/// ``<output_dir>/abstraction.png``.
#[pyfunction]
fn visualize_abstraction(py_world: Vec<Vec<String>>, output_dir: &str) -> PyResult<()> {
    let world = py_to_world(py_world)?;
    let world_size = world.len() as u32;

    // Render a 500×500 abstraction, computing cell size from dimensions
    let cell_size = 500 / world_size;

    let dir = Path::new(output_dir);
    let out_file = dir.join("abstraction.png");
    let out_path_str = out_file
        .to_str()
        .ok_or_else(|| PyRuntimeError::new_err("Invalid output path"))?;

    let game = Game::new(world.clone())
        .map_err(|e| PyRuntimeError::new_err(format!("abstraction failed: {:?}", e)))?;
    let (states, clusters) =
        get_abstraction(&game).map_err(|_| PyRuntimeError::new_err("Failed to get abstraction"))?;

    draw_abstraction(&world, &states, &clusters, out_path_str, cell_size)
        .map_err(|_| PyRuntimeError::new_err("Plotting error"))?;
    println!("Saved abstraction to: {:?}", out_path_str);

    Ok(())
}

/// Generate multiple textual/JSON representations of the map for prompting.
#[pyfunction]
fn generate_representations_py(py: Python, py_world: Vec<Vec<String>>) -> PyResult<PyObject> {
    // Reconstruct the Game
    let world = py_world
        .into_iter()
        .map(|row| row.into_iter().map(|s| s.chars().next().unwrap()).collect())
        .collect();
    let mut game =
        Game::new(world).map_err(|e| PyRuntimeError::new_err(format!("invalid world: {:?}", e)))?;
    // Generate representations
    let (js, txt, adj) = generate_representations(&mut game);
    // Convert JSON values to strings for Python
    let json_str = serde_json::to_string(&js)
        .map_err(|e| PyRuntimeError::new_err(format!("json serialization error: {}", e)))?;
    let adj_str = serde_json::to_string(&adj)
        .map_err(|e| PyRuntimeError::new_err(format!("adj serialization error: {}", e)))?;
    // Build a Python dict
    let dict = PyDict::new(py);
    dict.set_item("json", json_str)?;
    dict.set_item("text", txt)?;
    dict.set_item("adj", adj_str)?;
    // Return it as a PyObject
    Ok(dict.into_py(py))
}

/// Build transition and reward matrices along with the learned abstraction.
#[pyfunction]
fn generate_mdp(py: Python<'_>, py_world: Vec<Vec<String>>) -> PyResult<PyObject> {
    let world = py_to_world(py_world)?;

    let game =
        Game::new(world).map_err(|e| PyRuntimeError::new_err(format!("invalid world: {:?}", e)))?;

    let (states, clusters) = get_abstraction(&game)
        .map_err(|e| PyRuntimeError::new_err(format!("abstraction failed: {:?}", e)))?;
    let actions = [Action::Up, Action::Down, Action::Left, Action::Right];

    let (t, r) = build_matrices(&game, &states, &actions);

    let dict = PyDict::new(py);
    dict.set_item("T", t.clone().into_py(py))?;
    dict.set_item("R", r.clone().into_py(py))?;
    dict.set_item("abstraction", clusters.clone().into_py(py))?;

    Ok(dict.into_py(py))
}

/// Return the total number of reachable ground states in the map.
#[pyfunction]
fn get_number_of_states(py_world: Vec<Vec<String>>) -> PyResult<usize> {
    let world = py_to_world(py_world)?;
    let game =
        Game::new(world).map_err(|e| PyRuntimeError::new_err(format!("invalid world: {:?}", e)))?;

    let all_states = get_all_states(&game)
        .map_err(|e| PyRuntimeError::new_err(format!("abstraction failed: {:?}", e)))?;
    let num_states = all_states.len();

    Ok(num_states)
}

/// Python module initializer for `core_rust`.
#[pymodule]
fn core_rust(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<PyRunner>()?;

    m.add_function(wrap_pyfunction!(max_returns, m)?)?;

    m.add_function(wrap_pyfunction!(min_turns, m)?)?;

    m.add_function(wrap_pyfunction!(visualize_world_map, m)?)?;

    m.add_function(wrap_pyfunction!(visualize_abstraction, m)?)?;

    m.add_function(wrap_pyfunction!(generate_representations_py, m)?)?;

    m.add_function(wrap_pyfunction!(generate_mdp, m)?)?;

    m.add_function(wrap_pyfunction!(get_number_of_states, m)?)?;

    Ok(())
}

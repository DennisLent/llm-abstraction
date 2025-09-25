use std::collections::{HashSet, VecDeque};

use crate::core::abstraction::errors::AbstractionError;
use crate::core::game::*;
use game_logic::Game;
use state::State;

/// Compute shortest path (in turns) to the goal using BFS.
#[allow(dead_code)]
pub fn min_turns_to_finish(game: &Game) -> Result<usize, AbstractionError> {
    let mut visited: HashSet<State> = HashSet::new();
    let mut queue: VecDeque<(State, usize)> = VecDeque::new();

    // Seed BFS with the initial state at depth 0
    let start = game.get_state();
    queue.push_back((start.clone(), 0));
    visited.insert(start);

    while let Some((state, depth)) = queue.pop_front() {
        if state.unit_position == game.goal() {
            return Ok(depth);
        }

        // Otherwise expand its neighbors
        for &action in state.valid_moves().iter() {
            let (next_state, _) =
                game.simulate(&state, &action)
                    .map_err(|e| AbstractionError::Computation {
                        error: e.to_string(),
                    })?;

            // Only enqueue unseen states
            if visited.insert(next_state.clone()) {
                queue.push_back((next_state, depth + 1));
            }
        }
    }

    // If BFS exhausts without finding a terminal, no solution
    Err(AbstractionError::BFSExhausted)
}

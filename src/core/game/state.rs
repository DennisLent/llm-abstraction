use crate::core::game::utils::actions;
use actions::Action;
use serde::{Deserialize, Serialize};

/// MDP state: agent position plus available actions (optionally indexed).
#[derive(Debug, Clone, Hash, Eq, PartialEq, Serialize, Deserialize)]
pub struct State {
    pub unit_position: (usize, usize),
    pub valid_moves: Vec<Action>,
    pub index: Option<isize>,
}

impl State {
    /// Create a new state at the given position with the provided action set.
    pub fn new(unit_position: (usize, usize), valid_moves: Vec<Action>) -> Self {
        Self {
            unit_position,
            valid_moves,
            index: None,
        }
    }

    /// Borrow the valid actions for this state.
    pub fn valid_moves(&self) -> &Vec<Action> {
        &self.valid_moves
    }
}

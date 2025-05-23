use crate::core::game::utils::actions;
use actions::Action;
use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Hash, Eq, PartialEq, Serialize, Deserialize)]
pub struct State {
    pub unit_position: (usize, usize),
    pub valid_moves: Vec<Action>,
    pub index: Option<isize>,
}

impl State {
    pub fn new(unit_position: (usize, usize), valid_moves: Vec<Action>) -> Self {
        return Self {
            unit_position: unit_position,
            valid_moves: valid_moves,
            index: None,
        };
    }

    pub fn valid_moves(&self) -> &Vec<Action> {
        return &self.valid_moves;
    }
}

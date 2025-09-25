use super::actions::Action;
use crate::core::game::state::State;
use thiserror::Error;

/// Errors raised by invalid gridworld configurations or illegal simulation steps.
#[derive(Debug, Error)]
pub enum GameError {
    #[error("Invalid world configuration: world must be non-empty and square")]
    WorldShapeError,

    #[error("Invalid world configuration: tile character {character:?} not recognized")]
    InvalidTileCharacter { character: char },

    #[error("Invalid world configuration: two goals provided")]
    DuplicateGoal,

    #[error("Invalid world configuration: no goal provided")]
    MissingGoal,

    #[error("Simulation Error: Attempted illegal game‐logic operation")]
    GameLogicError,

    #[error("Simulation Error: Unit not found on the field")]
    UnitNotFound,

    #[error{"Simulation Error: Invalud action {action:?}"}]
    InvalidAction { action: Action },

    #[error("Simulation Error: invalid action {action:?} in state {state:?}")]
    InvalidStateAction { action: Action, state: State },

    #[error("Simulation Error: Invalid action id {id:?}")]
    InvalidActionId { id: usize },

    #[error("Simulation Error: Move out of bounds to ({x}, {y})")]
    OutOfBounds { x: isize, y: isize },
}

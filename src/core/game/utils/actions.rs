use super::errors::GameError;
use serde::{Deserialize, Serialize};

/// Available actions in the gridworld.
///
/// - Ground moves: Up, Down, Left, Right
/// - A no-op: `Nothing`
/// - Abstract actions: `AbstractAction1..8` are used when acting in the abstract MDP.
///   In a well-formed abstraction, an abstract state typically exposes 2–4 actions.
/// - `Root` is a sentinel used for the MCTS tree root.
#[derive(Debug, Clone, Copy, Hash, Eq, PartialEq, Serialize, Deserialize)]
pub enum Action {
    Up = 0,
    Down = 1,
    Left = 2,
    Right = 3,
    Nothing = 4,
    AbstractAction1 = 5,
    AbstractAction2 = 6,
    AbstractAction3 = 7,
    AbstractAction4 = 8,
    AbstractAction5 = 9,
    AbstractAction6 = 10,
    AbstractAction7 = 11,
    AbstractAction8 = 12,
    Root = 13,
}

impl Action {
    /// Numeric identifier of this action.
    pub fn id(&self) -> usize {
        *self as usize
    }

    /// Convert a numeric identifier back into an `Action`.
    pub fn from_id(id: usize) -> Result<Self, GameError> {
        match id {
            0 => Ok(Action::Up),
            1 => Ok(Action::Down),
            2 => Ok(Action::Left),
            3 => Ok(Action::Right),
            4 => Ok(Action::Nothing),
            5 => Ok(Action::AbstractAction1),
            6 => Ok(Action::AbstractAction2),
            7 => Ok(Action::AbstractAction3),
            8 => Ok(Action::AbstractAction4),
            9 => Ok(Action::AbstractAction5),
            10 => Ok(Action::AbstractAction6),
            11 => Ok(Action::AbstractAction7),
            12 => Ok(Action::AbstractAction8),
            value => Err(GameError::InvalidActionId { id: value }),
        }
    }
}

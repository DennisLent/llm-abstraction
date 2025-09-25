/// Per-step environment feedback returned by the simulator.
#[derive(Debug, Clone, Copy)]
pub struct GameVars {
    pub turn: i32,
    pub score: f32,
    pub done: bool,
}

impl GameVars {
    /// Convenience constructor.
    pub fn new(turn: i32, score: f32, done: bool) -> Self {
        GameVars { turn, score, done }
    }
}

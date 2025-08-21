#[derive(Debug, Clone, Copy)]
pub struct GameVars {
    pub turn: i32,
    pub score: f32,
    pub done: bool,
}

impl GameVars {
    pub fn new(turn: i32, score: f32, done: bool) -> Self {
        GameVars { turn, score, done }
    }
}

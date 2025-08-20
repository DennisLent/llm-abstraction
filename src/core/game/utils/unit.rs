#[derive(Debug, Clone, Copy)]
pub struct Unit {
    x: usize,
    y: usize,
    movement_points: i8,
    symbol: char,
}

impl Default for Unit {
    fn default() -> Self {
        Self::new()
    }
}

impl Unit {
    pub fn new() -> Self {
        Unit {
            x: 0,
            y: 0,
            movement_points: 1,
            symbol: '@',
        }
    }

    pub fn get_symbol(self) -> char {
        self.symbol
    }

    pub fn deduct_movement(&mut self) {
        self.movement_points -= 1;
    }

    pub fn get_movement(self) -> i8 {
        self.movement_points
    }

    pub fn reset_movement(&mut self) {
        self.movement_points = 1;
    }

    pub fn get_position(self) -> (usize, usize) {
        (self.x, self.y)
    }

    pub fn set_position(&mut self, x: usize, y: usize) {
        self.x = x;
        self.y = y;
    }
}

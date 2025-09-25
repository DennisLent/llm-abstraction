/// The controllable unit moving on the grid.
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
    /// Create a unit at (0,0) with one movement point and symbol '@'.
    pub fn new() -> Self {
        Unit {
            x: 0,
            y: 0,
            movement_points: 1,
            symbol: '@',
        }
    }

    /// Symbol used when printing the world.
    pub fn get_symbol(self) -> char {
        self.symbol
    }

    /// Consume one movement point.
    pub fn deduct_movement(&mut self) {
        self.movement_points -= 1;
    }

    /// Remaining movement points.
    pub fn get_movement(self) -> i8 {
        self.movement_points
    }

    /// Reset movement to one point.
    pub fn reset_movement(&mut self) {
        self.movement_points = 1;
    }

    /// Current coordinates `(x, y)`.
    pub fn get_position(self) -> (usize, usize) {
        (self.x, self.y)
    }

    /// Set coordinates to `(x, y)`.
    pub fn set_position(&mut self, x: usize, y: usize) {
        self.x = x;
        self.y = y;
    }
}

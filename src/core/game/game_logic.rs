use crate::core::game::utils::{actions, errors, unit, world};
use actions::Action;
use errors::GameError;
use unit::Unit;
use world::{Tile, World};

use crate::core::game::{game_variables, state};
use game_variables::GameVars;
use state::State;

#[derive(Debug, Clone)]
pub struct Game {
    _world_configuration: Vec<Vec<char>>,
    world: World,
    unit: Unit,
    turn: i32,
}

impl Game {
    pub fn new(world_vector: Vec<Vec<char>>) -> Result<Self, GameError> {
        let mut world = World::new(&world_vector)?;

        let unit = Unit::new();

        world.place_unit(unit);

        Ok(Game {
            world,
            unit,
            _world_configuration: world_vector,
            turn: 0,
        })
    }

    pub fn tile(&mut self, x: usize, y: usize) -> &Tile {
        self.world.get_tile(x, y)
    }

    pub fn print(&self) {
        println!("T: {}", self.turn);
        self.world.print();
    }

    pub fn get_size(&self) -> usize {
        self.world.size
    }

    pub fn reset(&mut self) {
        // We can unwrap here because we know that if we were able to generate before we can generate again
        self.world = World::new(&self._world_configuration).unwrap();
        self.unit = Unit::new();
        self.world.place_unit(self.unit);
        self.turn = 0;
    }

    pub fn check_game_done(&self) -> bool {
        self.unit.get_position() == self.world.goal
    }

    fn get_score(&self) -> f32 {
        if self.unit.get_position() == self.world.goal {
            return 1.0;
        }
        0.0
    }

    pub fn goal(&self) -> (usize, usize) {
        self.world.goal
    }

    pub fn world_configuration(&self) -> Vec<Vec<char>> {
        self._world_configuration.clone()
    }

    fn move_unit(&mut self, action: &Action) -> Result<(), GameError> {
        if self.unit.get_movement() <= 0 {
            return Ok(());
        }

        let (dx, dy): (isize, isize) = match action {
            Action::Up => (0, -1),
            Action::Down => (0, 1),
            Action::Left => (-1, 0),
            Action::Right => (1, 0),
            _ => {
                return Err(GameError::InvalidAction { action: *action });
            }
        };

        let (old_x, old_y) = self.unit.get_position();
        let (new_x, new_y) = (old_x as isize + dx, old_y as isize + dy);

        // Unit would move out of bounds, we just don't move it and keep it in place
        if new_x < 0
            || new_y < 0
            || new_x >= self.world.size as isize
            || new_y >= self.world.size as isize
        {
            self.unit.deduct_movement();
            return Ok(());
        }
        // New position is within bounds so we try to move the unit
        let (new_x_u, new_y_u) = (new_x as usize, new_y as usize);
        if self.world.get_tile(new_x_u, new_y_u).is_walkable() {
            match self.world.remove_unit() {
                Ok(()) => {
                    self.unit.set_position(new_x_u, new_y_u);
                    self.world.place_unit(self.unit);
                }
                Err(e) => {
                    return Err(e);
                }
            }
        }

        Ok(())
    }

    pub fn get_state(&self) -> State {
        let valid_moves = vec![Action::Up, Action::Down, Action::Left, Action::Right];
        let unit_position = self.unit.get_position();
        State::new(unit_position, valid_moves)
    }

    pub fn step(&mut self, action: &Action) -> Result<(State, GameVars), GameError> {
        match self.move_unit(action) {
            Ok(()) => {
                self.turn += 1;
                self.unit.reset_movement();
                let return_tuple = (
                    self.get_state(),
                    GameVars::new(self.turn, self.get_score(), self.check_game_done()),
                );
                Ok(return_tuple)
            }
            Err(e) => Err(e),
        }
    }

    fn set_state(&mut self, state: &State) -> Result<(), GameError> {
        let (new_x, new_y) = state.unit_position;
        match self.world.remove_unit() {
            Ok(()) => {
                self.unit.set_position(new_x, new_y);
                self.world.place_unit(self.unit);
                self.unit.reset_movement();
                Ok(())
            }
            Err(e) => Err(e),
        }
    }

    pub fn simulate(
        &self,
        initial_state: &State,
        action: &Action,
    ) -> Result<(State, GameVars), GameError> {
        let mut copied_game = self.clone();
        match copied_game.set_state(initial_state) {
            Ok(()) => match copied_game.step(action) {
                Ok((state, game_variables)) => Ok((state, game_variables)),
                Err(e) => Err(e),
            },
            Err(e) => Err(e),
        }
    }
}

use super::errors::GameError;
use super::unit::Unit;

#[derive(Debug, Clone, Copy)]
pub enum Terrain {
    Grass,
    Mountain,
    Goal,
}

#[derive(Debug, Clone, Copy)]
pub struct Tile {
    _x: usize,
    _y: usize,
    terrain: Terrain,
    walkable: bool,
    unit: Option<Unit>,
}

impl Tile {
    pub fn new(x: usize, y: usize, terrain: Terrain) -> Self {
        let walkable: bool = match terrain {
            Terrain::Mountain => false,
            _ => true,
        };

        return Tile {
            _x: x,
            _y: y,
            terrain: terrain,
            walkable: walkable,
            unit: None,
        };
    }

    pub fn is_walkable(self) -> bool {
        return self.walkable;
    }

    pub fn is_occupied(self) -> bool {
        match self.unit {
            Some(_unit) => return true,
            None => return false,
        }
    }

    pub fn place_unit(&mut self, unit: Unit) {
        self.unit = Some(unit)
    }

    pub fn remove_unit(&mut self) {
        self.unit = None
    }

    pub fn terrain(&self) -> Terrain {
        return self.terrain;
    }
}

#[derive(Debug, Clone)]
pub struct World {
    pub size: usize,
    tiles: Vec<Vec<Tile>>,
    pub goal: (usize, usize),
}

impl World {
    pub fn new(world_vector: &Vec<Vec<char>>) -> Result<Self, GameError> {
        let rows = world_vector.len();
        if rows == 0 {
            return Err(GameError::WorldShapeError);
        }

        for (_, row) in world_vector.iter().enumerate() {
            if row.len() != rows {
                return Err(GameError::WorldShapeError);
            }
        }

        let mut tiles: Vec<Vec<Tile>> = Vec::with_capacity(rows);
        let mut goal_location: Option<(usize, usize)> = None;

        for i in 0..rows {
            let world_row = &world_vector[i];
            // if you want to enforce a square world: replace with `cols`
            let mut tile_row: Vec<Tile> = Vec::with_capacity(world_row.len());

            for j in 0..world_row.len() {
                let terrain = match world_row[j] {
                    '.' => Terrain::Grass,
                    'X' => Terrain::Mountain,
                    'G' => {
                        // mark goal
                        if goal_location.is_some() {
                            // two goals? fail
                            return Err(GameError::DuplicateGoal);
                        }
                        goal_location = Some((i, j));
                        Terrain::Goal
                    }
                    character => {
                        // invalid character
                        return Err(GameError::InvalidTileCharacter {
                            character: character,
                        });
                    }
                };

                tile_row.push(Tile::new(i, j, terrain));
            }

            tiles.push(tile_row);
        }

        // ensure we found exactly one goal
        let goal = goal_location.ok_or(GameError::MissingGoal)?;

        Ok(World {
            size: rows,
            tiles,
            goal,
        })
    }

    pub fn print(&self) {
        let cell_width = 5;
        let size = self.size;

        print!("     ");
        for col in 0..size {
            print!("{:^width$}", col, width = cell_width);
        }
        println!();

        let hor = format!("  +{}+", "-".repeat(cell_width).repeat(size));
        println!("{}", hor);

        for (y, row) in self.tiles.iter().enumerate() {
            print!("{:<2}|", y);

            for tile in row {
                let symbol = if let Some(unit) = &tile.unit {
                    unit.get_symbol().to_string()
                } else {
                    match tile.terrain {
                        Terrain::Grass => "·".into(),
                        Terrain::Mountain => "X".into(),
                        Terrain::Goal => "G".into(),
                    }
                };
                print!("{:^width$}|", symbol, width = cell_width);
            }
            println!();

            println!("{}", hor);
        }
    }

    fn get_unit_position(&mut self) -> Result<(usize, usize), GameError> {
        for (y, row) in self.tiles.iter().enumerate() {
            for (x, tile) in row.iter().enumerate() {
                if tile.is_occupied() {
                    return Ok((x, y));
                }
            }
        }
        return Err(GameError::UnitNotFound);
    }

    pub fn place_unit(&mut self, unit: Unit) {
        let (x, y) = unit.get_position();
        self.tiles[y][x].place_unit(unit);
    }

    pub fn remove_unit(&mut self) -> Result<(), GameError> {
        let (x, y) = match self.get_unit_position() {
            Ok((x, y)) => (x, y),
            Err(e) => return Err(e),
        };

        self.tiles[y][x].remove_unit();

        return Ok(());
    }

    pub fn get_tile(&mut self, x: usize, y: usize) -> &Tile {
        return &self.tiles[y][x];
    }
}

use std::collections::HashMap;

use crate::core::{
    abstraction::homomorphism::get_all_states, game::game_logic::Game, game::utils::world::Terrain,
};
use serde_json::{json, Value};

#[allow(dead_code)]
fn generate_json_representation(game: &Game) -> Value {
    let size = game.get_size();

    let all_states = get_all_states(game).expect("failed to retrieve all staes in representation");

    let mut position_to_id = HashMap::new();

    for (index, state) in all_states.iter().enumerate() {
        position_to_id.insert(state.unit_position, index);
    }

    let mut grid = Vec::with_capacity(size);

    for y in 0..size {
        let mut row = Vec::with_capacity(size);
        for x in 0..size {
            if let Some(&idx) = position_to_id.get(&(x, y)) {
                row.push(json!(idx));
            } else {
                row.push(json!("X"));
            }
        }
        grid.push(row);
    }

    // start & goal
    let start_pos = (0, 0);
    let start = *position_to_id.get(&start_pos).expect("start not found");
    let goal_pos = game.goal();
    let goal = *position_to_id.get(&goal_pos).expect("goal not found");

    json!({
        "start": start,
        "goal":  goal,
        "grid":  grid,
    })
}

#[allow(dead_code)]
fn generate_text_representation(game: &mut Game) -> String {
    let size = game.get_size();
    let all_states = get_all_states(game).expect("failed to enumerate states");
    let mut pos2idx = HashMap::new();
    for (i, st) in all_states.iter().enumerate() {
        pos2idx.insert(st.unit_position, i);
    }

    let mut lines = Vec::with_capacity(size);
    for y in 0..size {
        let mut cells = Vec::with_capacity(size);
        for x in 0..size {
            match game.tile(x, y).terrain() {
                Terrain::Mountain => {
                    cells.push("X".to_string());
                }
                _ if pos2idx.contains_key(&(x, y)) => {
                    cells.push(pos2idx[&(x, y)].to_string());
                }
                _ => {
                    cells.push("?".to_string());
                }
            }
        }
        lines.push(cells.join(" "));
    }
    lines.join("\n")
}

#[allow(dead_code)]
fn generate_adjacency_representation(game: &mut Game) -> Value {
    let size = game.get_size();
    let all_states = get_all_states(game).expect("failed to enumerate states");
    let mut pos2idx = HashMap::new();
    for (i, st) in all_states.iter().enumerate() {
        pos2idx.insert(st.unit_position, i);
    }

    // start & goal
    let start_pos = (0, 0);
    let start = *pos2idx.get(&start_pos).expect("start not found");
    let goal_pos = game.goal();
    let goal = *pos2idx.get(&goal_pos).expect("goal not found");

    // directions: up/down/left/right
    let deltas = [(0_i32, -1_i32), (0, 1), (-1, 0), (1, 0)];

    // build adjacency map
    let mut state_adj = serde_json::Map::new();
    for ((x, y), &idx) in &pos2idx {
        let mut neigh = Vec::new();
        for &(dx, dy) in &deltas {
            let nx = *x as i32 + dx;
            let ny = *y as i32 + dy;
            if nx >= 0 && ny >= 0 && nx < size as i32 && ny < size as i32 {
                let (nx, ny) = (nx as usize, ny as usize);
                if game.tile(nx, ny).is_walkable() {
                    if let Some(&j) = pos2idx.get(&(nx, ny)) {
                        neigh.push(json!(j));
                    }
                }
            }
        }
        state_adj.insert(idx.to_string(), Value::Array(neigh));
    }

    json!({
        "start": start,
        "goal":  goal,
        "state adjacency": Value::Object(state_adj),
    })
}

#[allow(dead_code)]
pub fn generate_representations(game: &mut Game) -> (Value, String, Value) {
    let js = generate_json_representation(game);
    let txt = generate_text_representation(game);
    let adj = generate_adjacency_representation(game);
    (js, txt, adj)
}

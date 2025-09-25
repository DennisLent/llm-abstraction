use crate::core::game::*;
use game_logic::Game;
use state::State;
use utils::actions::Action;

/// Build a dense 3D indicator tensor T[s][a][s'] == 1 for legal transitions.
#[allow(dead_code)]
fn build_state_action_transition_matrix(
    game: &Game,
    all_states: &[State],
    all_actions: &[Action],
) -> Vec<Vec<Vec<usize>>> {
    let num_states = all_states.len();
    let num_actions = all_actions.len();

    // precompute a fast lookup from unit_position → state_idx
    let mut pos2idx = std::collections::HashMap::with_capacity(num_states);
    for (i, st) in all_states.iter().enumerate() {
        pos2idx.insert(st.unit_position, i);
    }

    // allocate: [S][A][S] zeroed
    let mut t = vec![vec![vec![0; num_states]; num_actions]; num_states];

    for (s_idx, state) in all_states.iter().enumerate() {
        for (a_idx, &action) in all_actions.iter().enumerate() {
            let (next_state, _) = game.simulate(state, &action).expect("simulation failed");

            if let Some(&ns_idx) = pos2idx.get(&next_state.unit_position) {
                t[s_idx][a_idx][ns_idx] = 1;
            }
        }
    }

    t
}

/// Build a dense reward matrix R[s][a] for one-step rewards.
#[allow(dead_code)]
fn build_state_action_reward_matrix(
    game: &Game,
    all_states: &[State],
    all_actions: &[Action],
) -> Vec<Vec<f32>> {
    let num_states = all_states.len();
    let num_actions = all_actions.len();

    // allocate: [S][A] zeroed
    let mut r = vec![vec![0.0; num_actions]; num_states];

    for (s_idx, state) in all_states.iter().enumerate() {
        for (a_idx, &action) in all_actions.iter().enumerate() {
            let (_next_state, game_vars) =
                game.simulate(state, &action).expect("simulation failed");
            r[s_idx][a_idx] = game_vars.score;
        }
    }

    r
}

/// Build transition and reward matrices for the provided states/actions.
#[allow(dead_code)]
pub fn build_matrices(
    game: &Game,
    all_states: &[State],
    all_actions: &[Action],
) -> (Vec<Vec<Vec<usize>>>, Vec<Vec<f32>>) {
    let transition_matrix = build_state_action_transition_matrix(game, all_states, all_actions);
    let reward_matrix = build_state_action_reward_matrix(game, all_states, all_actions);

    (transition_matrix, reward_matrix)
}

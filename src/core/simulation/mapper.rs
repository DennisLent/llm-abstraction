use crate::core::abstraction::*;
use crate::core::game::*;
use std::collections::HashMap;
use std::collections::HashSet;

use errors::AbstractionError;
use game_logic::Game;
use homomorphism::{get_abstraction, get_all_states};

use state::State;
use utils::actions::Action;

#[derive(Debug, Clone)]
pub struct Mapper {
    all_ground_states: Vec<State>,
    abstraction: Vec<Vec<isize>>,
    _abstract_transition_map: HashMap<(isize, Action), usize>,
    abstract_action_map: HashMap<(isize, Action), Action>,
    abstract_to_ground_map: HashMap<(usize, Action), (isize, Action)>,
}

impl Mapper {
    pub fn new(
        game: &Game,
        abstraction: Option<Vec<Vec<isize>>>,
    ) -> Result<Self, AbstractionError> {
        let (ground_states, abstraction) = match abstraction {
            Some(abstraction) => {
                let states = get_all_states(game).map_err(|e| AbstractionError::Computation {
                    error: e.to_string(),
                })?;
                (states, abstraction)
            }
            None => {
                let (states, abstraction) =
                    get_abstraction(game).map_err(|e| AbstractionError::Computation {
                        error: e.to_string(),
                    })?;
                (states, abstraction)
            }
        };

        let transition_map: HashMap<(isize, Action), usize> =
            Mapper::build_abstract_transition_map(&game, &ground_states, &abstraction)?;

        let (abstract_action_map, abstract_to_ground_map) =
            Self::build_action_maps(&transition_map, &abstraction)?;
        // println!("actions: {:?}\n", abstract_action_map);

        return Ok(Mapper {
            all_ground_states: ground_states,
            abstraction: abstraction,
            _abstract_transition_map: transition_map,
            abstract_action_map: abstract_action_map,
            abstract_to_ground_map: abstract_to_ground_map,
        });
    }

    fn get_ground_id(state: &State, all_states: &Vec<State>) -> isize {
        let state_id = all_states
            .iter()
            .find(|&ground_state| ground_state.unit_position == state.unit_position)
            .expect("No matching state")
            .index
            .expect("Gound state list did not generate with ids");
        return state_id;
    }

    fn build_abstract_transition_map(
        game: &Game,
        ground_states: &Vec<State>,
        abstraction: &Vec<Vec<isize>>,
    ) -> Result<HashMap<(isize, Action), usize>, AbstractionError> {
        let mut abstract_transition_map: HashMap<(isize, Action), usize> = HashMap::new();
        let ground_actions = [Action::Up, Action::Down, Action::Left, Action::Right];

        for ground_state in ground_states.clone() {
            let ground_state_index = match ground_state.index {
                Some(index) => index,
                None => Mapper::get_ground_id(&ground_state, &ground_states),
            };
            for ground_action in ground_actions {
                let (next_ground_state, _) =
                    game.simulate(&ground_state, &ground_action).map_err(|e| {
                        AbstractionError::Computation {
                            error: e.to_string(),
                        }
                    })?;
                let next_ground_state_id =
                    Mapper::get_ground_id(&next_ground_state, &ground_states);
                let next_abtract_state_id = abstraction
                    .iter()
                    .position(|cluster| cluster.contains(&next_ground_state_id))
                    .expect("ground state id not found in abstraction");
                abstract_transition_map
                    .insert((ground_state_index, ground_action), next_abtract_state_id);
            }
        }

        return Ok(abstract_transition_map);
    }

    fn build_action_maps(
        transition_map: &HashMap<(isize, Action), usize>,
        abstraction: &[Vec<isize>],
    ) -> Result<
        (
            HashMap<(isize, Action), Action>,
            HashMap<(usize, Action), (isize, Action)>,
        ),
        AbstractionError,
    > {
        let mut ga2aa = HashMap::new();
        let mut aa2ga = HashMap::new();
        let ground_actions = [Action::Up, Action::Down, Action::Left, Action::Right];

        for (src_abs, cluster) in abstraction.iter().enumerate() {
            // 1) bucket all (gs,ga) by next_abs
            let mut buckets: Vec<(usize, Vec<(isize, Action)>)> = Vec::new();
            for &gs in cluster {
                for &ga in &ground_actions {
                    let next_abs = transition_map[&(gs, ga)];
                    if let Some((_, ref mut vec)) = buckets.iter_mut().find(|(k, _)| *k == next_abs)
                    {
                        vec.push((gs, ga));
                    } else {
                        buckets.push((next_abs, vec![(gs, ga)]));
                    }
                }
            }

            // 2) assign abstract‐action IDs in that insertion order
            let mut next_aa = 5; // AbstractAction1 == 5
            for (_next_abs, pairs) in buckets {
                let aa = Action::from_id(next_aa).map_err(|e| AbstractionError::Computation {
                    error: e.to_string(),
                })?;
                next_aa += 1;

                // **new**: pick the pair whose gs is minimal
                let &(rep_gs, rep_ga) = pairs
                    .iter()
                    .min_by_key(|(gs, _)| *gs)
                    .expect("bucket never empty");

                // record the reverse mapping once
                aa2ga.entry((src_abs, aa)).or_insert((rep_gs, rep_ga));

                // lift that same aa onto *every* pair in this bucket
                for (gs, ga) in pairs {
                    ga2aa.insert((gs, ga), aa);
                }
            }
        }

        Ok((ga2aa, aa2ga))
    }

    pub fn ground_state_to_abstract(&self, state: &State) -> State {
        let ground_state_id = Mapper::get_ground_id(&state, &self.all_ground_states);

        let abstract_id = self
            .abstraction
            .iter()
            .position(|cluster| cluster.contains(&ground_state_id))
            .expect("ground state not in any cluster") as isize;

        let mut set = HashSet::new();
        for &ground_action in state.valid_moves().iter() {
            if let Some(&abstract_action) = self
                .abstract_action_map
                .get(&(ground_state_id, ground_action))
            {
                set.insert(abstract_action);
            }
        }
        let valid_abstract_moves: Vec<Action> = set.into_iter().collect();

        let mut abstract_state = State::new(state.unit_position, valid_abstract_moves);
        abstract_state.index = Some(abstract_id);
        return abstract_state;
    }

    pub fn abstract_state_action_to_ground(
        &self,
        state: &State,
        action: Action,
    ) -> (State, Action) {
        let abs_id = state.index.expect("abstract state needs an index") as usize;
        let (gs, ga) = if let Some(&(gs, ga)) = self.abstract_to_ground_map.get(&(abs_id, action)) {
            (gs, ga)
        } else {
            // fallback: pick the cluster representative and loop in place
            let cluster = &self.abstraction[abs_id];
            let &rep_gs = cluster
                .iter()
                .min()
                .expect("cluster should have at least one state");

            // scan in fixed order for a move that stays in this abstract state
            let ground_moves = [Action::Up, Action::Down, Action::Left, Action::Right];
            let ga = ground_moves
                .iter()
                .copied()
                .find(|&ga| {
                    self._abstract_transition_map
                        .get(&(rep_gs, ga))
                        .copied()
                        .expect("every (gs,ga) must be in transition_map")
                        == abs_id
                })
                .expect("no looping move found for abstract state");

            (rep_gs, ga)
        };

        // build the new ground‐state
        let mut ground_state = self.all_ground_states[gs as usize].clone();
        ground_state.index = Some(gs);
        (ground_state, ga)
    }
}

mod tests {
    use super::*;

    #[allow(dead_code)]
    fn make_game() -> Game {
        let world = vec![
            vec!['.', '.', '.'],
            vec!['.', '.', '.'],
            vec!['.', '.', 'G'],
        ];

        return Game::new(world).expect("failed to build test game");
    }

    #[test]
    fn test_mapper_init_no_abstraction() {
        let game = make_game();

        let mapper = Mapper::new(&game, None).unwrap();

        let expected = vec![
            vec![0],
            vec![1, 2],
            vec![3, 5],
            vec![4],
            vec![6, 7],
            vec![8],
        ];
        assert_eq!(mapper.abstraction, expected);
    }

    #[test]
    fn test_mapper_init_with_abstraction() {
        let game = make_game();

        let supplied = vec![
            vec![0],
            vec![1, 2],
            vec![3],
            vec![4],
            vec![5],
            vec![6, 7],
            vec![8],
        ];
        let mapper = Mapper::new(&game, Some(supplied.clone())).unwrap();
        assert_eq!(mapper.abstraction, supplied);
    }

    #[test]
    fn test_all_states() {
        let game = make_game();

        let all_states = get_all_states(&game).unwrap();
        assert_eq!(all_states.len(), 9)
    }

    #[test]
    fn test_state_mapping() {
        let game = make_game();

        let all_states = get_all_states(&game).unwrap();

        let mapper = Mapper::new(&game, None).unwrap();

        for (i, state) in all_states.iter().enumerate() {
            let ground_id = i;
            assert_eq!(ground_id as usize, i);

            let abstract_idx = mapper
                .ground_state_to_abstract(&state.clone())
                .index
                .unwrap() as usize;

            let want_idx = mapper
                .abstraction
                .iter()
                .position(|cluster| cluster.contains(&(ground_id as isize)))
                .unwrap();
            assert_eq!(abstract_idx, want_idx);
        }
    }

    #[test]
    fn test_abstract_action_transitions() {
        // build the 3×3 world with goal in bottom-right
        let world = vec![
            vec!['.', '.', '.'],
            vec!['.', '.', '.'],
            vec!['.', '.', 'G'],
        ];
        let game = Game::new(world).unwrap();
        let mapper = Mapper::new(&game, None).unwrap();

        // (initial_abs_state, abstract_action, expected_abs_state)
        let cases = vec![
            (0, Action::AbstractAction1, 0),
            (0, Action::AbstractAction2, 1),
            (1, Action::AbstractAction1, 0),
            (1, Action::AbstractAction2, 2),
            (1, Action::AbstractAction3, 1),
            (1, Action::AbstractAction4, 3),
            (2, Action::AbstractAction1, 1),
            (2, Action::AbstractAction2, 2),
            (2, Action::AbstractAction3, 4),
            (3, Action::AbstractAction1, 1),
            (3, Action::AbstractAction2, 4),
            (4, Action::AbstractAction1, 3),
            (4, Action::AbstractAction2, 4),
            (4, Action::AbstractAction3, 2),
            (4, Action::AbstractAction4, 5),
            (5, Action::AbstractAction2, 5),
        ];

        for (init_abs, aa, want_abs) in cases {
            // pick the “representative” ground state from that cluster
            let gs_id = mapper.abstraction[init_abs][0] as usize;
            let ground_state = &mapper.all_ground_states[gs_id];

            // embed ground → abstract
            let abstract_state = mapper.ground_state_to_abstract(ground_state);

            // abstract action → ground action
            let (_sel_gs, ground_action) =
                mapper.abstract_state_action_to_ground(&abstract_state, aa);

            // simulate one step at the ground level
            let (new_ground_state, _) = game.simulate(ground_state, &ground_action).unwrap();

            // map back up
            let new_abs_state = mapper.ground_state_to_abstract(&new_ground_state);
            let got_abs = new_abs_state.index.unwrap() as usize;

            assert_eq!(
                got_abs, want_abs,
                "From abstract state {} via {:?}, expected {} but got {}",
                init_abs, aa, want_abs, got_abs
            );
        }
    }

    #[test]
    fn test_abstract_action_transitions_4x4() {
        // build the 4×4 world with goal at (3,3)
        let world = vec![
            vec!['.', '.', '.', '.'],
            vec!['.', '.', '.', '.'],
            vec!['.', '.', '.', '.'],
            vec!['.', '.', '.', 'G'],
        ];
        let game = Game::new(world).unwrap();
        let mapper = Mapper::new(&game, None).unwrap();

        // (initial_abs_state, abstract_action, expected_abs_state)
        let cases = vec![
            (0, Action::AbstractAction1, 0),
            (0, Action::AbstractAction2, 1),
            (1, Action::AbstractAction1, 0),
            (1, Action::AbstractAction2, 2),
            (1, Action::AbstractAction3, 1),
            (1, Action::AbstractAction4, 3),
            (2, Action::AbstractAction1, 1),
            (2, Action::AbstractAction2, 4),
            (2, Action::AbstractAction3, 2),
            (2, Action::AbstractAction4, 5),
            (3, Action::AbstractAction1, 1),
            (3, Action::AbstractAction2, 5),
            (4, Action::AbstractAction1, 2),
            (4, Action::AbstractAction2, 4),
            (4, Action::AbstractAction3, 6),
            (5, Action::AbstractAction1, 3),
            (5, Action::AbstractAction2, 6),
            (5, Action::AbstractAction3, 2),
            (5, Action::AbstractAction4, 7),
            (6, Action::AbstractAction1, 5),
            (6, Action::AbstractAction2, 6),
            (6, Action::AbstractAction3, 4),
            (6, Action::AbstractAction4, 8),
            (7, Action::AbstractAction1, 5),
            (7, Action::AbstractAction2, 8),
            (8, Action::AbstractAction1, 7),
            (8, Action::AbstractAction2, 8),
            (8, Action::AbstractAction3, 6),
            (8, Action::AbstractAction4, 9),
            (9, Action::AbstractAction2, 9),
        ];

        for (init_abs, aa, want_abs) in cases {
            // pick the first ground-state in that cluster
            let gs_id = mapper.abstraction[init_abs][0] as usize;
            let ground_state = &mapper.all_ground_states[gs_id];

            // embed to abstract
            let abstract_state = mapper.ground_state_to_abstract(ground_state);

            // choose ground action from abstract action
            let (_sel_gs, ground_action) =
                mapper.abstract_state_action_to_ground(&abstract_state, aa);

            // simulate one step at the ground level
            let (new_ground_state, _) = game.simulate(ground_state, &ground_action).unwrap();

            // map back up
            let new_abs_state = mapper.ground_state_to_abstract(&new_ground_state);
            let got_abs = new_abs_state.index.unwrap() as usize;

            assert_eq!(
                got_abs, want_abs,
                "From abstract state {} via {:?}, expected {} but got {}",
                init_abs, aa, want_abs, got_abs
            );
        }
    }

    #[test]
    fn test_abstract_to_ground_uses_minimum_representative_3() {
        let game = make_game();
        let mapper = Mapper::new(&game, None).expect("failed to build Mapper");

        // pull out both the full ground‐state list and the clusters
        let (all_states, clusters) = get_abstraction(&game).expect("homomorphism failed");

        // for each abstract‐state cluster ...
        for (abs_id, cluster) in clusters.iter().enumerate() {
            // cluster is sorted, so the first element is the minimum ground‐id
            let rep_ground_id = cluster[0];

            // get the abstract State object by starting from that representative
            let rep_state = &all_states[rep_ground_id as usize];
            let abs_state = mapper.ground_state_to_abstract(rep_state);
            assert_eq!(
                abs_state.index.unwrap() as usize,
                abs_id,
                "representative state had wrong abstract index"
            );

            // for every abstract‐action available in this abstract‐state ...
            for &abs_action in abs_state.valid_moves().iter() {
                // map back to a ground‐state & ground‐action
                let (gs, _ga) = mapper.abstract_state_action_to_ground(&abs_state, abs_action);
                let mapped_id = Mapper::get_ground_id(&gs, &all_states);

                // **this** must equal the minimal ground_id for the cluster
                assert_eq!(
                    mapped_id, rep_ground_id,
                    "abstract state {abs_id}, action {abs_action:?} mapped back to ground \
                     {mapped_id} but expected the minimal representative {rep_ground_id}"
                );
            }
        }
    }

    #[test]
    fn test_abstract_to_ground_uses_minimum_representative_4() {
        let world = vec![
            vec!['.', '.', '.', '.'],
            vec!['.', '.', '.', '.'],
            vec!['.', '.', '.', '.'],
            vec!['.', '.', '.', 'G'],
        ];

        let game = Game::new(world).unwrap();
        let mapper = Mapper::new(&game, None).expect("failed to build Mapper");

        // pull out both the full ground‐state list and the clusters
        let (all_states, clusters) = get_abstraction(&game).expect("homomorphism failed");

        // for each abstract‐state cluster ...
        for (abs_id, cluster) in clusters.iter().enumerate() {
            // cluster is sorted, so the first element is the minimum ground‐id
            let rep_ground_id = cluster[0];

            // get the abstract State object by starting from that representative
            let rep_state = &all_states[rep_ground_id as usize];
            let abs_state = mapper.ground_state_to_abstract(rep_state);
            assert_eq!(
                abs_state.index.unwrap() as usize,
                abs_id,
                "representative state had wrong abstract index"
            );

            // for every abstract‐action available in this abstract‐state ...
            for &abs_action in abs_state.valid_moves().iter() {
                // map back to a ground‐state & ground‐action
                let (gs, _ga) = mapper.abstract_state_action_to_ground(&abs_state, abs_action);
                let mapped_id = Mapper::get_ground_id(&gs, &all_states);

                // **this** must equal the minimal ground_id for the cluster
                assert_eq!(
                    mapped_id, rep_ground_id,
                    "abstract state {abs_id}, action {abs_action:?} mapped back to ground \
                     {mapped_id} but expected the minimal representative {rep_ground_id}"
                );
            }
        }
    }
}

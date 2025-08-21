use crate::core::agent::mcts::MCTSAgent;
use crate::core::*;
use game::game_logic::Game;
use ordered_float::Pow;
use simulation::mapper::Mapper;
use simulation::simulator::{AbstractSim, GroundSim, Simulator};

pub struct Runner {
    game: Game,
    mapper: Option<Mapper>,
}

impl Runner {
    pub fn new(game: &Game, abstracted: bool, abstraction: Option<Vec<Vec<isize>>>) -> Self {
        let mapper = if abstracted {
            Some(Mapper::new(game, abstraction).unwrap())
        } else {
            None
        };

        Runner {
            game: game.clone(),
            mapper,
        }
    }

    fn compute_discounted_returns(gamma: f32, turns_taken: i32) -> f32 {
        gamma.pow(turns_taken)
    }

    pub fn run(
        &mut self,
        sim_limit: i32,
        sim_depth: i32,
        c: f32,
        gamma: f32,
        seed: Option<u64>,
        max_turns: i32,
        runs: usize,
        debug: bool,
        show_mcts: bool,
    ) -> Vec<(i32, f32, (usize, usize))> {
        let mut results = Vec::with_capacity(runs);

        for run_idx in 0..runs {
            // pick the right simulator once
            let simulator: Box<dyn Simulator> = if let Some(mapper) = &self.mapper {
                Box::new(AbstractSim::new(&self.game, mapper.clone()))
            } else {
                Box::new(GroundSim::new(&self.game))
            };

            let mut agent = MCTSAgent::new(sim_limit, sim_depth, c, gamma, seed, simulator);

            // track one local state through the turns
            let mut current_state = self.game.get_state();
            let mut game_done = false;

            for turn in 1..=max_turns {
                if debug {
                    println!(
                        "[Run {} Turn {}] State unit position = {:?}",
                        run_idx, turn, current_state.unit_position
                    );
                }

                // MCTS returns an Action (abstract or ground)
                let action = if let Some(mapper) = &self.mapper {
                    let abs_action = agent.run(current_state.clone(), debug, show_mcts);
                    let abs_state = mapper.ground_state_to_abstract(&current_state);
                    let (_, ground_action) =
                        mapper.abstract_state_action_to_ground(&abs_state, abs_action);
                    ground_action
                } else {
                    agent.run(current_state.clone(), debug, show_mcts)
                };

                // simulate that action via the same Simulator
                let (next_state, game_vars) = self.game.step(&action).unwrap_or_else(|err| {
                        panic!("Runner simulation error at run {}, turn: {}:\nState: {:?}\nAction: {:?}\nError: {:?}", run_idx, turn, current_state, action, err)
                    });

                if game_vars.done {
                    let score = Self::compute_discounted_returns(gamma, turn);
                    if debug {
                        println!(
                            "[Run {}] finished in {} turns, score = {}",
                            run_idx, turn, score
                        );
                    }
                    results.push((turn, score, next_state.unit_position));
                    game_done = true;
                    break;
                }

                current_state = next_state;
            }

            if !game_done {
                // ran all the way to max_turns without finishing
                if debug {
                    println!(
                        "[Run {}] hit turn limit = {}, score = 0",
                        run_idx, max_turns
                    );
                }
                results.push((max_turns, 0.0, current_state.unit_position));
            }

            // reset the underlying world for the NEXT run
            self.game.reset();
        }

        results
    }
}

#[cfg(test)]
mod runner_tests {
    use super::*;
    use crate::core::game::game_logic::Game;

    /// Helper to build a simple 3×3 world with goal in bottom‐right.
    fn make_game() -> Game {
        let world = vec![
            vec!['.', '.', '.'],
            vec!['.', '.', '.'],
            vec!['.', '.', 'G'],
        ];
        Game::new(world).unwrap()
    }

    #[test]
    fn test_runner_max_turns_zero() {
        let game = make_game();
        // ground simulation, no abstraction
        let mut runner = Runner::new(&game, false, None);

        // max_turns = 0: we should get exactly `runs` entries of (0,0.0)
        let runs = 5;
        let out = runner.run(
            /*sim_limit=*/ 1, /*sim_depth=*/ 1, /*c=*/ 1.0, /*gamma=*/ 1.0,
            /*seed=*/ None, /*max_turns=*/ 0, /*runs=*/ runs, /*debug=*/ false,
            /*show_mcts=*/ false,
        );
        assert_eq!(out.len(), runs);
        assert!(out.iter().all(|&(t, s, _)| t == 0 && s == 0.0));
    }

    #[test]
    fn test_runner_one_turn_timeout() {
        let game = make_game();
        let mut runner = Runner::new(&game, false, None);

        // max_turns = 1: in one step you can never reach the goal,
        // so every run should return (1, 0.0).
        let runs = 3;
        let out = runner.run(1, 1, 1.0, 1.0, None, 1, runs, false, false);
        assert_eq!(out.len(), runs);
        assert!(out.iter().all(|&(t, s, _)| t == 1 && s == 0.0));
    }

    #[test]
    fn test_runner_identity_abstraction_equivalent_to_ground() {
        // Both with simulation high simulation limit should be able to find th end and be able to find the goal perfectly in a 3 by 3
        let game = make_game();

        // ground runner
        let mut ground_runner = Runner::new(&game, false, None);
        let ground_out = ground_runner.run(128, 16, 1.4, 0.85, None, 10, 1, false, false);

        // abstract runner with identity abstraction (each state in its own cluster)
        let identity_clusters: Vec<Vec<isize>> = (0..9).map(|i| vec![i]).collect();
        let mut abs_runner = Runner::new(&game, true, Some(identity_clusters));
        let abs_out = abs_runner.run(128, 16, 1.4, 0.85, None, 10, 1, false, false);

        // should both have the same score
        assert_eq!(ground_out, abs_out);
    }
}

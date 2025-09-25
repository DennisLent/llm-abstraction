use std::cell::RefCell;
use std::rc::Rc;

use crate::core::agent::node::{MCTSError, MCTSNode, NodeRef};
use crate::core::game::*;
use crate::core::simulation::simulator::{Simulator, SimulatorType};
use ordered_float::Pow;
use rand::prelude::*;
use rand::{Rng, SeedableRng};
use state::State;
use utils::actions::Action;

/// Simple Monte Carlo Tree Search agent parameterized by a `Simulator`.
#[derive(Debug, Clone)]
pub struct MCTSAgent<S: Simulator> {
    simulation_limit: i32,
    simulation_depth: i32,
    c: f32,
    gamma: f32,
    index_count: i32,
    rng: StdRng,
    simulator: S,
}

impl<S: Simulator> MCTSAgent<S> {
    /// Create a new agent with the given search budget and parameters.
    pub fn new(
        simulation_limit: i32,
        simulation_depth: i32,
        c: f32,
        gamma: f32,
        seed: Option<u64>,
        simulator: S,
    ) -> Self {
        let rng = match seed {
            Some(value) => StdRng::seed_from_u64(value),
            None => StdRng::from_os_rng(),
        };

        MCTSAgent {
            simulation_limit,
            simulation_depth,
            c,
            gamma,
            index_count: 0,
            rng,
            simulator,
        }
    }

    fn choose_random_action(&mut self, state: &State) -> Action {
        let valid_actions = state.valid_moves();
        let idx = self.rng.random_range(0..valid_actions.len());
        valid_actions[idx]
    }

    /// Perform a default-policy rollout from `start_node` for at most `remaining_depth`.
    fn rollout(&mut self, start_node: &NodeRef, remaining_depth: i32, debug: bool) -> f32 {
        if debug {
            println!(
                "Rollout node {:?} with budget {:?}",
                start_node.borrow(),
                remaining_depth
            )
        };

        if start_node.borrow().is_terminal() || remaining_depth <= 0 {
            if debug {
                println!("ROLLOUT ABORTED: Terminal node or no budget")
            }
            return 0.0;
        }

        let node_state = start_node.borrow().get_state();
        let mut total_reward: f32 = 0.0;

        for depth in 1..=remaining_depth {
            let action = self.choose_random_action(&node_state);
            let (state, game_vars) = self.simulator.simulate(&node_state, action);
            let reward = game_vars.score;

            total_reward += (self.gamma.pow(depth - 1)) * reward;

            if debug {
                println!("Rollout step {:?}: {:?} -> {:?}", depth, action, state);
                println!(
                    "Rollout step {:?}: R = {:?}, tot_reward += {:?}^{:?} * {:?}",
                    depth,
                    game_vars.score,
                    self.gamma,
                    depth - 1,
                    reward
                );
                println!(
                    "Rollout step {:?}: Total reward = {:?}",
                    depth, total_reward
                );
            }

            if game_vars.done {
                if debug {
                    println!(
                        "Rollout terminated at step {:?} with total_reward = {:?}",
                        depth, total_reward
                    )
                }
                return total_reward;
            }
        }

        total_reward
    }

    /// Expand one untried action from `node` and return the new child.
    fn expansion(&mut self, node: &NodeRef, debug: bool) -> Result<NodeRef, MCTSError> {
        let action = {
            let mut n = node.borrow_mut();
            n.expand(&mut self.rng)
        };
        let (state_before, depth) = {
            let n = node.borrow();
            (n.get_state(), n.get_depth() + 1)
        };

        if debug {
            println!(
                "Expanding node {:?} with action {:?}",
                node.borrow(),
                action
            )
        };

        let (new_state, game_vars) = self.simulator.simulate(&state_before, action);

        let idx = self.index_count;
        let child = MCTSNode::new(
            new_state,
            Some(Rc::downgrade(node)),
            action,
            depth,
            game_vars.score,
            game_vars.done,
            idx,
            self.c,
            self.gamma,
        );
        let child_rc = Rc::new(RefCell::new(child));

        node.borrow_mut().add_child(Rc::clone(&child_rc));
        self.index_count += 1;

        Ok(child_rc)
    }

    /// Run one MCTS iteration and return the best action from the root.
    pub fn run(&mut self, state: State, debug: bool, show_mcts: bool) -> Action {
        let initial_state = match self.simulator.simulator_type() {
            SimulatorType::Ground => {
                if debug {
                    println!("Running MCTS in ground")
                }
                state
            }
            SimulatorType::Abstract => {
                if debug {
                    println!("Running MCTS in abstract")
                }
                self.simulator.get_initial_state(state)
            }
        };

        let root = Rc::new(RefCell::new(MCTSNode::new(
            initial_state,
            None,
            Action::Root,
            0,
            0.0,
            false,
            self.index_count,
            self.c,
            self.gamma,
        )));

        let limit = self.simulation_limit as usize;
        for _ in 0..limit {
            let leaf = MCTSNode::find_leaf_node(&root);
            if debug {
                println!("selected node: {:?}", leaf.borrow())
            }

            {
                let depth = leaf.borrow().get_depth();
                let remaining = self.simulation_depth - depth;
                if remaining > 0 && !leaf.borrow().is_terminal() {
                    self.index_count += 1;

                    let child = self.expansion(&leaf, debug).expect("expand should succeed");

                    let value = self.rollout(&child, remaining - 1, debug);

                    MCTSNode::backpropagate(&child, value);
                }
            }
        }

        if debug || show_mcts {
            MCTSNode::print_tree(&root);
            println!("{}", "-".repeat(40));
        }

        let best_action = root.borrow().best_action();
        best_action
    }
}

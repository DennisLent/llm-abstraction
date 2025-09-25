use crate::core::game::*;
use crate::core::simulation::*;
use game_logic::Game;
use game_variables::GameVars;
use mapper::Mapper;
use state::State;
use utils::actions::Action;

/// Indicates whether a simulator operates on ground or abstract states.
pub enum SimulatorType {
    Ground,
    Abstract,
}

/// Minimal interface for pluggable simulators used by MCTS.
pub trait Simulator {
    /// Simulate one step from `state` with `action`, returning the next state and game vars.
    fn simulate(&self, state: &State, action: Action) -> (State, GameVars);

    /// Whether this simulator works at the ground or abstract level.
    fn simulator_type(&self) -> SimulatorType;

    /// Transform a ground state into the appropriate simulator’s initial state.
    fn get_initial_state(&self, state: State) -> State;
}

impl Simulator for Box<dyn Simulator> {
    fn simulate(&self, state: &State, action: Action) -> (State, GameVars) {
        (**self).simulate(state, action)
    }

    fn simulator_type(&self) -> SimulatorType {
        (**self).simulator_type()
    }

    fn get_initial_state(&self, state: State) -> State {
        (**self).get_initial_state(state)
    }
}

/// Simulator that steps the ground MDP directly.
#[derive(Debug, Clone)]
pub struct GroundSim {
    game: Game,
}

impl GroundSim {
    pub fn new(game: &Game) -> Self {
        GroundSim { game: game.clone() }
    }
}

impl Simulator for GroundSim {
    fn simulate(&self, state: &State, action: Action) -> (State, GameVars) {
        let (s, vars) = self.game.simulate(state, &action).unwrap();
        (s, vars)
    }

    fn simulator_type(&self) -> SimulatorType {
        SimulatorType::Ground
    }

    fn get_initial_state(&self, state: State) -> State {
        state
    }
}

/// Simulator that maps abstract actions to ground actions via a `Mapper`.
#[derive(Debug, Clone)]
pub struct AbstractSim {
    game: Game,
    mapper: Mapper,
}

impl AbstractSim {
    pub fn new(game: &Game, mapper: Mapper) -> Self {
        AbstractSim {
            game: game.clone(),
            mapper,
        }
    }
}

impl Simulator for AbstractSim {
    fn simulate(&self, state: &State, action: Action) -> (State, GameVars) {
        // Map abstract action to ground, simulate, and lift back
        let (ground_state, ground_action) =
            self.mapper.abstract_state_action_to_ground(state, action);
        let (new_ground_state, vars) = self.game.simulate(&ground_state, &ground_action).unwrap();
        let abs_state = self.mapper.ground_state_to_abstract(&new_ground_state);
        (abs_state, vars)
    }

    fn simulator_type(&self) -> SimulatorType {
        SimulatorType::Abstract
    }

    fn get_initial_state(&self, state: State) -> State {
        self.mapper.ground_state_to_abstract(&state)
    }
}

use crate::core::game::*;
use crate::core::simulation::*;
use game_logic::Game;
use game_variables::GameVars;
use mapper::Mapper;
use state::State;
use utils::actions::Action;

pub enum SimulatorType {
    Ground,
    Abstract,
}

pub trait Simulator {
    fn simulate(&self, state: &State, action: Action) -> (State, GameVars);

    fn simulator_type(&self) -> SimulatorType;

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

#[derive(Debug, Clone)]
pub struct GroundSim {
    game: Game,
}

impl GroundSim {
    pub fn new(game: &Game) -> Self {
        return GroundSim { game: game.clone() };
    }
}

impl Simulator for GroundSim {
    fn simulate(&self, state: &State, action: Action) -> (State, GameVars) {
        let (s, vars) = self.game.simulate(state, &action).unwrap();
        return (s, vars);
    }

    fn simulator_type(&self) -> SimulatorType {
        return SimulatorType::Ground;
    }

    fn get_initial_state(&self, state: State) -> State {
        return state;
    }
}

#[derive(Debug, Clone)]
pub struct AbstractSim {
    game: Game,
    mapper: Mapper,
}

impl AbstractSim {
    pub fn new(game: &Game, mapper: Mapper) -> Self {
        return AbstractSim {
            game: game.clone(),
            mapper: mapper,
        };
    }
}

impl Simulator for AbstractSim {
    fn simulate(&self, state: &State, action: Action) -> (State, GameVars) {
        // println!(
        //     "Mapping abstract state-action: ({:?}, {:?})",
        //     state.unit_position, action
        // );
        let (ground_state, ground_action) =
            self.mapper.abstract_state_action_to_ground(state, action);
        // println!(
        //     "Mapped to: ({:?}, {:?})",
        //     ground_state.unit_position, ground_action
        // );
        let (new_ground_state, vars) = self.game.simulate(&ground_state, &ground_action).unwrap();
        let abs_state = self.mapper.ground_state_to_abstract(&new_ground_state);
        return (abs_state, vars);
    }

    fn simulator_type(&self) -> SimulatorType {
        return SimulatorType::Abstract;
    }

    fn get_initial_state(&self, state: State) -> State {
        return self.mapper.ground_state_to_abstract(&state);
    }
}

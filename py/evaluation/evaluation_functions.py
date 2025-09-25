from .mcts import run_mcts, run_mcts_llm
from .saving import map_to_filename
import os

def mcts_evaluation(simulation_limits: list[int], 
                    simulation_depths: list[int], 
                    world: list[list[int]], 
                    runner_configs: list[tuple],
                    folder_name: str, 
                    runs: int = 100,
                    c: float = 1.4,
                    gamma: float = 0.85,
                    debug: bool = False,
                    show_mcts: bool = False) -> None:
    """Run MCTS sweeps and save results.

    Parameters
    ----------
    simulation_limits : list of int
        Candidate simulation budgets for MCTS.
    simulation_depths : list of int
        Candidate roll-out depths for MCTS.
    world : list of list of int
        Grid world specification.
    runner_configs : list of tuple
        Runner specifications as tuples ``(abstracted: bool, abstraction: list[list[int]] | None, label: str)``.
    folder_name : str
        Output subfolder under ``outputs/``.
    runs : int, optional
        Number of repetitions per configuration, by default 100.
    c : float, optional
        UCT exploration constant, by default 1.4.
    gamma : float, optional
        Discount factor used in MCTS, by default 0.85.
    debug : bool, optional
        If ``True``, enable verbose debug output.
    show_mcts : bool, optional
        If ``True``, print the MCTS tree during simulation.

    Returns
    -------
    None
        Saves map visualizations and CSV/plots under ``outputs/<folder_name>/<map_hash>``.
    """

    map_name = map_to_filename(world=world, extension=None)
    output_path = os.path.join('outputs', f'{folder_name}', map_name)
    run_mcts(world=world, 
            configs=runner_configs, 
            sim_limits=simulation_limits, 
            sim_depths=simulation_depths,
            output_path=output_path, 
            runs=runs,
            c=c,
            gamma=gamma, 
            debug=debug, 
            show_mcts=show_mcts)


def mcts_llm_evaluation(simulation_limits: list[int], 
                        simulation_depths: list[int], 
                        world: list[list[int]], 
                        runner_configs: list[tuple],
                        folder_name: str,
                        prompt_index: int,
                        model: str, 
                        runs: int = 100,
                        c: float = 1.4,
                        gamma: float = 0.85,
                        debug: bool = False,
                        show_mcts: bool = False) -> None:
    """Run MCTS sweeps including the best LLM abstraction and save results.

    Parameters
    ----------
    simulation_limits : list of int
        Candidate simulation budgets for MCTS.
    simulation_depths : list of int
        Candidate roll-out depths for MCTS.
    world : list of list of int
        Grid world specification.
    runner_configs : list of tuple
        Runner specifications as tuples ``(abstracted: bool, abstraction: list[list[int]] | None, label: str)``.
    folder_name : str
        Output subfolder under ``outputs/``.
    prompt_index : int
        Prompt index used to generate the LLM abstraction.
    model : str
        LLM model identifier used during abstraction generation.
    runs : int, optional
        Number of repetitions per configuration, by default 100.
    c : float, optional
        UCT exploration constant, by default 1.4.
    gamma : float, optional
        Discount factor used in MCTS, by default 0.85.
    debug : bool, optional
        If ``True``, enable verbose debug output.
    show_mcts : bool, optional
        If ``True``, print the MCTS tree during simulation.

    Returns
    -------
    None
        Saves CSV/plots under ``outputs/<folder_name>/<map_hash>`` with LLM identifiers in filenames.
    """

    map_name = map_to_filename(world=world, extension=None)
    output_path = os.path.join('outputs', f'{folder_name}', map_name)
    run_mcts_llm(world=world, 
                 configs=runner_configs, 
                 sim_limits=simulation_limits, 
                 sim_depths=simulation_depths,
                 output_path=output_path, 
                 prompt_index=prompt_index,
                 model=model,
                 runs=runs,
                 c=c,
                 gamma=gamma, 
                 debug=debug, 
                 show_mcts=show_mcts)

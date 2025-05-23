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
                    show_mcts: bool = False):
    """
    Main MCTS evaluation function that uses the rust_core library to run MCTS simulations for a given world and given agent specifications.

    Args
    -----
    - `simulation_limits` (list[int]): list of simulation limits to use for the MCTS simulation
    - `simulation_depths` (list[int]): list of simulation depths to use for the MCTS simulation
    - `world` (list[list[int]]): representation of the world (taken from the config file)
    - `runner_configs` (list[tuple]): further information about the type of agents (see example below)
    - `runs` (int): specify the number of times each agent gets tested on the map. Default is 100.
    - `c` (float): exploration constant used in MCTS. Default is 1.4.
    - `gamma` (float): discount factor used in MCTS. Default is 0.85.
    - `debug` (float): debug flag to show all the operations in Python and Rust. Be warned this generates a lot of output in Rust as it shows forward simulations,
    reward calculations, states and actions. It is recommended to parse the output into a separate log file. Default is False.

    Returns
    -----
    Saves the generated map, abstraction, MCTS results (as csv and image) in a folder in outputs using a generated hash name for uniqueness

    Example
    -----
    The following configuration will run a simple 3 by 3 world for both a ground agent, abstracted agent with the optimal abstraction calculated by the algorithm
    and an abstracted agent with a pre-determined abstracted over simulation limits from [8, 64] and simulation depths [8, 32] each gets run 100 times for each
    configuration.
    ```
    world = [
            ['.', '.', '.'],
            ['.', '.', '.'],
            ['.', '.', 'G']
            ]
    
    simulation_limits = [8, 16, 32, 64]
    simulation_depths = [8, 16, 32]

    # Specified as follows (abstracted: bool, abstraction: list[list[int]] | None, name: str)
    runner_configs = [
        (False, None, "Ground"),
        (True, None, "Ideal Abstraction")
        (True, [[0], [1], [2], [3], [4], [5], [6,7], [8]], "Given Abstraction")
    ]

    # Run
    mcts_evaluation(simulation_limits, simulation_depths, world, runner_configs)

    # CLI output
    >>> Saved world visualization to: "outputs/map_3x3_17aca6d680/map.png"
    >>> Saved abstraction to: "outputs/map_3x3_17aca6d680/abstraction.png"
    >>> Saved MCTS results to outputs/map_3x3_17aca6d680
    ```
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
                        show_mcts: bool = False):
    """
    Main MCTS evaluation function that uses the rust_core library to run MCTS simulations for a given world and given agent specifications.

    Args
    -----
    - `simulation_limits` (list[int]): list of simulation limits to use for the MCTS simulation
    - `simulation_depths` (list[int]): list of simulation depths to use for the MCTS simulation
    - `world` (list[list[int]]): representation of the world (taken from the config file)
    - `runner_configs` (list[tuple]): further information about the type of agents (see example below)
    - `runs` (int): specify the number of times each agent gets tested on the map. Default is 100.
    - `c` (float): exploration constant used in MCTS. Default is 1.4.
    - `gamma` (float): discount factor used in MCTS. Default is 0.85.
    - `debug` (float): debug flag to show all the operations in Python and Rust. Be warned this generates a lot of output in Rust as it shows forward simulations,
    reward calculations, states and actions. It is recommended to parse the output into a separate log file. Default is False.

    Returns
    -----
    Saves the generated map, abstraction, MCTS results (as csv and image) in a folder in outputs using a generated hash name for uniqueness

    Example
    -----
    The following configuration will run a simple 3 by 3 world for both a ground agent, abstracted agent with the optimal abstraction calculated by the algorithm
    and an abstracted agent with a pre-determined abstracted over simulation limits from [8, 64] and simulation depths [8, 32] each gets run 100 times for each
    configuration.
    ```
    world = [
            ['.', '.', '.'],
            ['.', '.', '.'],
            ['.', '.', 'G']
            ]
    
    simulation_limits = [8, 16, 32, 64]
    simulation_depths = [8, 16, 32]

    # Specified as follows (abstracted: bool, abstraction: list[list[int]] | None, name: str)
    runner_configs = [
        (False, None, "Ground"),
        (True, None, "Ideal Abstraction")
        (True, [[0], [1], [2], [3], [4], [5], [6,7], [8]], "Given Abstraction")
    ]

    # Run
    mcts_evaluation(simulation_limits, simulation_depths, world, runner_configs)

    # CLI output
    >>> Saved world visualization to: "outputs/map_3x3_17aca6d680/map.png"
    >>> Saved abstraction to: "outputs/map_3x3_17aca6d680/abstraction.png"
    >>> Saved MCTS results to outputs/map_3x3_17aca6d680
    ```
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
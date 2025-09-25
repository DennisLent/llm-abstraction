import matplotlib.pyplot as plt
from tqdm import tqdm
import numpy as np
import pandas as pd
from core_rust import PyRunner, max_returns, min_turns, visualize_world_map, visualize_abstraction
import os

# Lightweight SEM helper with SciPy fallback when available
try:  # pragma: no cover - trivial import fallback
    from scipy.stats import sem as _scipy_sem  # type: ignore

    def _sem(a):
        return float(_scipy_sem(a))
except Exception:  # SciPy not installed; compute SEM via NumPy

    def _sem(a):
        arr = np.asarray(a, dtype=float)
        n = arr.size
        if n <= 1:
            return 0.0
        return float(arr.std(ddof=1) / np.sqrt(n))

def run_mcts(world: list[list[str]],
            configs: list[tuple[str, bool, list[list[int]] | None]],
            sim_limits: list[int],
            sim_depths: list[int],
            output_path: str,
            runs: int = 100,
            c: float = 1.4,
            gamma: float = 0.85,
            debug: bool = False,
            show_mcts: bool = False) -> None:
    """Run MCTS sweeps and save raw results and plots.

    Parameters
    ----------
    world : list of list of str
        Grid world specification.
    configs : list of tuple
        Runner specifications as tuples ``(abstracted: bool, abstraction: list[list[int]] | None, label: str)``.
    sim_limits : list of int
        Candidate simulation budgets for MCTS.
    sim_depths : list of int
        Candidate roll-out depths for MCTS.
    output_path : str
        Directory where results will be saved.
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
    """
    
    # Save map using rust core
    visualize_world_map(world, output_path)
    visualize_abstraction(world, output_path)

    
    # Get maximum possible return (gamma^min_turns)
    max_return = max_returns(world, gamma)

    # Run simulations using rust core
    results = _run_sweep(world=world, 
                         configs=configs, 
                         sim_limits=sim_limits, 
                         sim_depths=sim_depths, 
                         runs=runs, 
                         c=c, 
                         gamma=gamma, 
                         debug=debug, 
                         show_mcts=show_mcts)
    
    
    if not os.path.isdir(output_path):
        os.mkdir(output_path)
    file_name = os.path.join(output_path, "raw_results.csv")
    results.to_csv(file_name)
    
    # Graph results
    _graph_results(results=results, 
                   runs=runs, 
                   max_return=max_return, 
                   output_path=output_path)

def run_mcts_llm(world: list[list[str]],
                 configs: list[tuple[str, bool, list[list[int]] | None]],
                 sim_limits: list[int],
                 sim_depths: list[int],
                 output_path: str,
                 prompt_index: int,
                 model: str,
                 runs: int = 100,
                 c: float = 1.4,
                 gamma: float = 0.85,
                 debug: bool = False,
                 show_mcts: bool = False) -> None:
    """Run MCTS sweeps with LLM identifier in output filenames.

    Parameters
    ----------
    world : list of list of str
        Grid world specification.
    configs : list of tuple
        Runner specifications as tuples ``(abstracted: bool, abstraction: list[list[int]] | None, label: str)``.
    sim_limits : list of int
        Candidate simulation budgets for MCTS.
    sim_depths : list of int
        Candidate roll-out depths for MCTS.
    output_path : str
        Directory where results will be saved.
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
    """

    # Get maximum possible return (gamma^min_turns)
    max_return = max_returns(world, gamma)

    # Run simulations using rust core
    results = _run_sweep(world=world, 
                         configs=configs, 
                         sim_limits=sim_limits, 
                         sim_depths=sim_depths, 
                         runs=runs, 
                         c=c, 
                         gamma=gamma, 
                         debug=debug, 
                         show_mcts=show_mcts)
    
    
    if not os.path.isdir(output_path):
        os.mkdir(output_path)
    file_name = os.path.join(output_path, f"{prompt_index}_{model}_raw_results.csv")
    results.to_csv(file_name)
    
    # Graph results
    _graph_results(results=results, 
                   runs=runs, 
                   max_return=max_return, 
                   output_path=output_path,
                   title_addition=(model, prompt_index))
    

def _run_sweep(world: list[list[str]],
              configs: list[tuple[str, bool, list[list[int]] | None]],
              sim_limits: list[int],
              sim_depths: list[int],
              runs: int = 100,
              c: float = 1.4,
              gamma: float = 0.85,
              seed: int | None = None,
              debug: bool = False,
              show_mcts: bool = False) -> pd.DataFrame:
    """Execute all sweeps and aggregate metrics into a DataFrame.

    Parameters
    ----------
    world : list of list of str
        Grid world specification.
    configs : list of tuple
        Runner specifications as tuples ``(abstracted: bool, abstraction: list[list[int]] | None, label: str)``.
    sim_limits : list of int
        Candidate simulation budgets for MCTS.
    sim_depths : list of int
        Candidate roll-out depths for MCTS.
    runs : int, optional
        Number of repetitions per configuration, by default 100.
    c : float, optional
        UCT exploration constant, by default 1.4.
    gamma : float, optional
        Discount factor used in MCTS, by default 0.85.
    seed : int or None, optional
        Random seed for the runner, by default ``None``.
    debug : bool, optional
        If ``True``, enable verbose debug output.
    show_mcts : bool, optional
        If ``True``, print the MCTS tree during simulation.

    Returns
    -------
    pandas.DataFrame
        One row per (agent, depth, limit) with mean and SEM statistics.
    """
    
    records = []

    # Total number simulations:
    total_runs = len(configs) * len(sim_depths) * len(sim_limits) * runs
    pbar = tqdm(total=total_runs, desc="All MCTS runs")

    # Loop over each
    for abstracted_bool, abstraction, label in configs:
        for depth in sim_depths:
            for limit in sim_limits:
                scores = []
                turns = []

                for i in range(runs):
                    runner = PyRunner(world, abstracted_bool, abstraction)
                    max_turns = 2 * len(world) + 2

                    # sim_limit, sim_depth, c, gamma, seed, max_turns, runs, debug, show_mcts
                    out = runner.run(limit, depth, c, gamma, seed, max_turns, 1, debug, show_mcts)

                    # print(f"{label} run {i} turns played: {out[0][0]} player position at end: {out[0][2]} score: {out[0][1]}")

                    scores.append(out[0][1])
                    turns.append(out[0][0])
                    pbar.update(1)

                records.append({
                    "agent_type": label,
                    "simulation_depth": depth,
                    "simulation_limit": limit,
                    "average_score": np.mean(scores),
                    "std_score": _sem(scores),
                    "average_turns": np.mean(turns),
                    "std_turns": _sem(turns)
                })

    pbar.close()
    return pd.DataFrame(records)

def _graph_results(results: pd.DataFrame, runs: int, max_return: float, output_path: str, title_addition: tuple = None) -> None:
    """Plot and save MCTS performance curves.

    Parameters
    ----------
    results : pandas.DataFrame
        Must include columns ``simulation_depth``, ``agent_type``, ``simulation_limit``,
        ``average_score``, and ``std_score``.
    runs : int
        Number of runs per configuration (used in the figure title).
    max_return : float
        The optimal return value plotted as a reference line.
    output_path : str
        Directory where the plot will be saved.
    title_addition : tuple, optional
        Optional ``(model, prompt_index)`` pair added to the title and filename.

    Returns
    -------
    None
    """
    depths = sorted(results['simulation_depth'].unique())

    fig, axes = plt.subplots(
        nrows=len(depths),
        ncols=1,
        figsize=(8, 4 * len(depths)),
        sharex=True,
        constrained_layout=True
    )
    # if there's only one depth, axes isn't a list
    if len(depths) == 1:
        axes = [axes]

    for ax, depth in zip(axes, depths):
        depth_df = results[results['simulation_depth'] == depth]

        # plot each agent type
        for agent in list(results["agent_type"].drop_duplicates()):
            agent_df = depth_df[depth_df['agent_type'] == agent]
            if agent_df.empty:
                continue
            agent_df = agent_df.sort_values('simulation_limit')
            ax.errorbar(
                agent_df['simulation_limit'],
                agent_df['average_score'],
                yerr=agent_df['std_score'],
                marker='o',
                capsize=5,
                label=agent.title()
            )

        # draw optimal‐return line
        ax.axhline(
            max_return,
            color='red',
            linestyle='--',
            label=f'Optimal Return ({max_return:.4f})'
        )

        # formatting
        ax.set_xlim(left=0)
        ax.set_ylim(0, 1.1 * max_return)
        ax.set_title(f"Simulation Depth = {depth}")
        ax.set_ylabel("Average Score")
        ax.grid(True, linestyle='--', alpha=0.5)
        ax.legend(loc='lower right')
    
    axes[-1].set_xlabel("Simulation Limit")

    agents = list(results["agent_type"].drop_duplicates())
    title_str = ' vs. '.join(agents)
    model, prompt_index = title_addition if title_addition else None, None

    title = f"MCTS Performance: {title_str}\n(averaged over {runs} runs)" if not title_addition else f"MCTS Performance: {title_str}\n{model} @ {prompt_index}\n(averaged over {runs} runs)"

    # overall title
    fig.suptitle(title, fontsize=14)

    # Each MCTS plot get's saved to map directory
    if not os.path.isdir(output_path):
        os.mkdir(output_path)
    if title_addition is None:
        file_name = os.path.join(output_path, f"mcts_results.png")
    else:
        model, prompt_index = title_addition
        file_name = os.path.join(output_path, f"{prompt_index}_{model}_mcts_results.png")
    plt.savefig(file_name)
    print(f"Saved MCTS results to {output_path}")

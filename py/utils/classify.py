from core_rust import get_number_of_states, generate_mdp


def classify_abstraction(world: list[list[str]]) -> str:
    """Classify abstractability based on state-space reduction.

    The classification compares the number of ground states to the number of
    abstract states produced by the MDP abstraction and returns a coarse
    label describing the relative reduction.

    Parameters
    ----------
    world : list of list of str
        Grid world description.

    Returns
    -------
    str
        One of ``"perfect abstraction"``, ``"partial abstraction"``, or
        ``"no abstraction"``.
    """
    n = get_number_of_states(world)
    mdp = generate_mdp(world)
    abstraction = mdp["abstraction"]
    
    k = len(abstraction)
    
    if n == 0:
        return "unknown"
    
    reduction = (n - k) / n
    
    if reduction >= 0.25:
        return "perfect abstraction"
    elif reduction > 0.0:
        return "partial abstraction"
    else:
        return "no abstraction"

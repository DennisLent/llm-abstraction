from core_rust import get_number_of_states, generate_mdp


def classify_abstraction(world: list[list[str]]) -> str:
    """
    Classifies the abstraction of a game based on how much it reduces the search space.
    
    It computes:
      - n: the total number of states (from get_all_possible_states(game))
      - k: the number of abstract states (from get_abstraction(game))
    
    Then the reduction factor is defined as (n - k) / n.
    
    For example, with your examples:
      - Perfect abstraction if k/n <= 0.3  (i.e. reduction factor >= 0.7)
      - Partial abstraction if 0.3 < k/n <= 0.7
      - No abstraction if k/n > 0.7
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
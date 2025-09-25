import numpy as np
from scipy.stats import wasserstein_distance


def bisimulation_similarity(
    candidate_clustering: list[list[int]],
    ideal_clustering:     list[list[int]],
    transitions:          np.ndarray,   # shape (S, A, S)
    rewards:              np.ndarray,   # shape (S, A)
    c:                    float = 0.5   # trade-off for Wasserstein distance
) -> float:
    """Compute similarity between two MDP abstractions in [0, 1].

    Uses a bisimulation-style distance (cf. García et al. 2022) based on
    reward differences and the 1-Wasserstein distance over abstract-state
    transition distributions, then maps distance to similarity via
    ``1 / (1 + d_M)``.

    Parameters
    ----------
    candidate_clustering : list of list of int
        Proposed abstract-state partition of ground states.
    ideal_clustering : list of list of int
        Reference (ideal) abstract-state partition.
    transitions : numpy.ndarray
        Transition tensor with shape ``(S, A, S)``.
    rewards : numpy.ndarray
        Reward matrix with shape ``(S, A)``.
    c : float, optional
        Trade-off in ``[0, 1]`` between reward and transition distances,
        by default 0.5.

    Returns
    -------
    float
        Similarity score in ``[0, 1]`` (1.0 means identical).
    """

    # Precompute abstract MDP from matrices given by the rust_core library
    def build_abstract_mdp(clusters: list[list[int]]):
        """Aggregate transitions and rewards over a given partition.

        Parameters
        ----------
        clusters : list of list of int
            Partition of ground states into ``K`` abstract states.

        Returns
        -------
        tuple of numpy.ndarray
            ``(T_hat, r_hat)`` where ``T_hat`` has shape ``(K, A, K)`` and
            ``r_hat`` has shape ``(K, A)``.
        """

        K = len(clusters)
        S, A, _ = transitions.shape

        # Initialize matrices
        T_hat = np.zeros((K, A, K), dtype=float) # T_hat[i,a,j] = avg_{s in Ci} sum_{s' in Cj} T[s,a,s']
        r_hat = np.zeros((K, A), dtype=float) # r_hat[i,a]    = avg_{s in Ci} R[s,a]

        # Iterate each abstract state
        for i, C in enumerate(clusters):
            Csize = max(len(C), 1)
            
            # sum rewards
            # rewards[C, :] has shape (|C|, A)
            r_hat[i] = rewards[C, :].sum(axis=0) / Csize

            # sum transitions
            # transitions[C, a, :] has shape (|C|, S)
            # we want for each a, the total flow into each Cj
            for a in range(A):

                P_sprime = transitions[C, a, :].sum(axis=0) / Csize # P_sprime[s'] = avg over s in C of T[s,a,s']
                
                # Aggregate P_sprime over each cluster Cj
                for j, Cj in enumerate(clusters):
                    
                    T_hat[i, a, j] = P_sprime[Cj].sum() # sum P_sprime[s'] over s' in Cj

        return T_hat, r_hat

    # Build both candidate and ideal abstract MDPs
    T_cand, r_cand = build_abstract_mdp(candidate_clustering)
    T_ideal, r_ideal = build_abstract_mdp(ideal_clustering)
    Kc, A, _ = T_cand.shape
    Ki, _, _ = T_ideal.shape

    # Abstract‐state “locations” on the line for Wasserstein metric
    positions_c = np.arange(Kc)
    positions_i = np.arange(Ki)

    # Compute pairwise abstract‐state distances d_S[i,j]
    # d_S[i,j] will hold the worst‐case (over actions) distance between i and j
    d_S = np.zeros((Kc, Ki), dtype=float)

    for i in range(Kc):
        for j in range(Ki):

            # worst-case over actions
            max_over_a = 0.0
            for a in range(A):

                # reward difference
                rd = abs(r_cand[i, a] - r_ideal[j, a])

                # transition distance via 1-Wasserstein
                # https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.wasserstein_distance.html
                P1 = T_cand[i, a, :]
                P2 = T_ideal[j, a, :]
                td = wasserstein_distance(
                    positions_c, positions_i,
                    P1, P2
                )

                # weighted combination 
                dist_ia = (1 - c) * rd + c * td
                if dist_ia > max_over_a:
                    max_over_a = dist_ia

            d_S[i, j] = max_over_a

    # Lift to full‐MDP distance via (directed) Hausdorff

    # for each candidate state i, find closest ideal j
    row_max = np.max(np.min(d_S, axis=1)) if Kc > 0 else 0.0

    # for each ideal state  j, find closest candidate i
    col_max = np.max(np.min(d_S, axis=0)) if Ki > 0 else 0.0

    d_M = max(row_max, col_max)

    # Map into similarity [0,1]
    similarity = 1.0 / (1.0 + d_M)  # perfect match ⇒ d_M=0 ⇒ sim=1.0

    return float(similarity)

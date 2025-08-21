# Bisimulation Metric

To rate an LLM‑derived clustering, the project computes a similarity score inspired by bisimulation metrics (Thesis). For two ground states \(s_i\) and \(s_j\) in different clusters:

1. Compare immediate rewards: \(|R(s_i,a) - R(s_j,a)|\).
2. Compare their transition distributions by lifting them to the abstract space. The ground distributions over next clusters are compared with a Wasserstein distance. A Hausdorff lift aggregates over actions.

The final distance \(d(s_i, s_j)\) is the maximum over actions of reward and transition differences. Similarity is then
\[
\text{sim}(s_i, s_j) = \frac{1}{1 + d(s_i, s_j)}.
\]

The **composite z‑score** evaluates an entire clustering by running agents with MCTS. We compute a model‑based score (above) and a performance score from planning returns. Each score is normalised to a z‑value and the difference \(z_s - z_g\) rewards clusters that preserve both theory and practice.

*Example:* if clustering merges symmetric corners, the bisimulation score is near 1 and MCTS returns match the ground agent, yielding a high composite value.

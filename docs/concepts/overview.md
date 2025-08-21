# Concept Overview

This project combines three ideas to evaluate abstractions of grid‑world environments (Thesis).

- **MDP Abstraction** – states of a Markov Decision Process are grouped into clusters that preserve behavior; see [MDPs & Abstraction](mdp_abstraction.md).
- **Bisimulation Metric** – candidate abstractions are scored by comparing rewards and transition distributions; see [Bisimulation Metric](bisimulation_metric.md).
- **MCTS with Abstraction** – abstract states shrink the search space for planning agents; see [MCTS & Abstraction](mcts.md).

These components allow LLM‑generated clusters to be evaluated both analytically and through planning performance.

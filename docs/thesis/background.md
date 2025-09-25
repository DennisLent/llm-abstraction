# Background

- MDPs: tuple ⟨S, A, P, R, γ⟩; policies; optimal policy (Thesis).
- Abstraction: mappings over states/actions; trade-offs; mechanisms (bisimulation, homomorphism, metrics) (Thesis).
- Approximate/lax bisimulation and homomorphism intuition; cluster focus (Thesis).
- Similarity metrics: structural (Wasserstein/EMD, Hausdorff-style lifting), behavioral (V/Q deltas), performance (Thesis).
- MCTS: 4 phases; where abstraction reduces branching; EMCTS idea (Thesis).
- LLMs used: LLaMA vs Deepseek‑R1 families; reasoning focus; hallucination/cohesion concerns (Thesis).

MDPs & Abstraction (migrated)
An episodic grid world can be described as an MDP (S, A, T, R, γ) where states are tile coordinates and actions move the agent. We abstract states by grouping them into clusters; actions remain unchanged. When two ground states fall into the same cluster, the planner treats them as equivalent. Homomorphism concepts motivate these clusters: transitions from a member of a cluster should lead to clusters in the same way, and cumulative rewards should match up to a tolerance (Thesis). For small grids this resembles a lax bisimulation: if two positions behave similarly with respect to the goal and obstacles, they can be merged. Cluster‑based abstractions are used rather than vector embeddings to keep the simulator stateless and retain clear semantics for each abstract state.

MCTS & Abstraction (migrated)
Monte Carlo Tree Search proceeds in four phases: selection, expansion, simulation, backpropagation. Abstract states reduce the branching factor because multiple ground states share a single node. The planner operates on abstract identifiers while the simulator translates them to concrete coordinates. The Rust Runner switches between abstract and ground actions on every turn using a mapping layer, letting MCTS reason over clusters without modifying the underlying environment.

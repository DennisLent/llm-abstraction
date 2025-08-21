# MDPs & Abstraction

An episodic grid world can be described as an MDP \((S, A, T, R, \gamma)\) where states are tile coordinates and actions move the agent. This project abstracts **states** by grouping them into clusters; actions remain unchanged. When two ground states fall into the same cluster, the planner treats them as equivalent.

Homomorphism concepts motivate these clusters: transitions from a member of a cluster should lead to clusters in the same way, and cumulative rewards should match up to a tolerance (Thesis). For small grids this resembles a lax bisimulation: if two positions behave similarly with respect to the goal and obstacles, they can be merged.

Example: in a 3×3 world with the goal at the bottom‑right, corner tiles other than the goal have symmetric behavior. A cluster \(\{(0,0), (0,2), (2,0)\}\) preserves optimal policies by mapping their transitions to equivalent abstract neighbors.

We use **cluster‑based abstractions** rather than vector embeddings to keep the simulator stateless and to retain clear semantics for each abstract state.

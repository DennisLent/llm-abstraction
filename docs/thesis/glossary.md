# Glossary

This glossary collects key terms used throughout the documentation. For precise definitions and discussion, see the Thesis PDF.

- MDP. A Markov Decision Process is a tuple ⟨S, A, P, R, γ⟩ that describes states, actions, transition dynamics, rewards, and discounting.
- MCTS. Monte Carlo Tree Search is a best‑first planning algorithm that iterates selection, expansion, simulation, and backpropagation to approximate the optimal policy.
- EMD/Wasserstein. The Earth Mover’s (1‑Wasserstein) distance measures how much probability mass must be moved to transform one distribution into another; we apply it to abstract‑state transition distributions.
- Abstraction. A clustering of ground states into a smaller set of abstract states intended to preserve planning‑relevant behavior.
- Homomorphism. A structure‑preserving mapping that relates transitions and rewards in the ground MDP to those in an abstract MDP.
- Composite z. A standardized summary that combines a model‑based similarity score with planning performance into a single ranking statistic.

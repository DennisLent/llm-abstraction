# Idea

- Problem: planning explodes in large state spaces; abstraction reduces branching and depth while preserving decision quality.
- Research question: can LLMs propose useful cluster abstractions for MDP planning? Sub‑questions: how close to ideal; how utility varies with model family/size, prompt style, and map structure.
- Contributions: (1) an extraction framework that composes prompts, queries models, self‑refines, cleans, and validates clusterings; (2) dual evaluation covering structure (model‑based metric) and downstream planning (MCTS) with a composite score.
- Scope: deterministic, fully observable gridworld; cluster partitions; MCTS planning.
- For: RL/Planning practitioners, LLM‑agent researchers, and research hiring managers.

See Repo → Architecture for how Python orchestration and the Rust core split responsibilities, and Thesis → Overview for a concise summary of findings. 

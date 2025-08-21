# LLM-Based State Abstraction

Rust backend for fast grid‑world simulation + Python orchestration for LLM abstraction and evaluation with MCTS.

Large language models cluster states of a grid world into abstract groups. The Rust core simulates environments and scoring while Python prompts models, cleans their output and evaluates agents with Monte Carlo Tree Search. This project demonstrates how symbolic planning and LLM reasoning can cooperate for efficient decision making (Thesis).

## Highlights

- **Stateless simulator in Rust** with Python runners.
- **LLM‑driven cluster abstractions** inspired by homomorphism ideas.
- **Dual metrics:** model‑based bisimulation score and performance‑based evaluation; combined into a composite *z* value.

See the [Quickstart](quickstart.md) to run an example or dive into the [Architecture](architecture/system.md) for design details.

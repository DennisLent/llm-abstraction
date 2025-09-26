# LLM-Based State Abstraction

Rust simulator + Python orchestration to test whether LLMs can produce useful MDP abstractions for planning (MCTS).

This project explores how large language models can induce useful state abstractions in a grid‑world environment and how these abstractions interact with classical planning. The performance‑critical simulation and representation building live in a Rust core, while Python orchestrates prompt construction, model calls, post‑processing and empirical evaluation. Together, they enable fast experiments that compare abstraction quality both by a model‑based similarity metric and by downstream planning performance using Monte Carlo Tree Search.

Highlights
- Stateless Rust core with Python orchestration
- LLM‑driven cluster abstractions (JSON or text representations)
- Model‑based similarity and MCTS performance metrics
- Composite score to rank models and prompts

Quick Links
- [Quickstart](repo/quickstart.md)
- [Architecture](repo/architecture.md)
- [Experiments & Results](thesis/experiments_results.md)

Project Links
- View on GitHub: https://github.com/DennisLent/llm-abstraction

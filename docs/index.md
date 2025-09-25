# LLM-Based State Abstraction

This project explores how large language models can induce useful state abstractions in a grid‑world environment and how these abstractions interact with classical planning. The performance‑critical simulation and representation building live in a Rust core, while Python orchestrates prompt construction, model calls, post‑processing and empirical evaluation. Together, they enable fast experiments that compare abstraction quality both by a model‑based similarity metric and by downstream planning performance using Monte Carlo Tree Search.

The Rust library provides deterministic environment dynamics, representation generation and scoring routines. Python composes prompts, normalises model outputs into clusterings and runs agents against the Rust core to measure how abstractions affect planning quality. This combination keeps the runtime tight and reproducible while retaining the flexibility needed for experimentation. A deeper discussion of the overall approach, motivation and findings is presented in the accompanying thesis.

Read the thesis inline at the [Thesis](thesis.md) page, or download it directly: [Thesis PDF](Thesis_v2_21_08_2025.pdf).

To try the system, start with the [Quickstart](quickstart.md). For a tour of the design, see the [Architecture](architecture/system.md) pages. API reference material for both languages is available under API, and the complete Rust crate documentation is available on the [Rust API](api/rust.md) page.

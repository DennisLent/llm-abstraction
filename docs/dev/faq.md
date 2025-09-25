# FAQ

**Q: Why Rust and Python?**

A: Rust offers deterministic, fast simulation and matrix generation. Python provides flexibility for prompt engineering and analysis.

**Q: Do I need internet access?**

A: Only for downloading Ollama models; the core simulation runs offline.

**Q: Can I add new maps?**

A: Yes. Add ASCII maps under `game:` in `config.yml` and run `preview-maps` to generate assets.

**Q: Which language models are used?**

A: The project uses locally hosted models via Ollama (e.g., Llama‑2 variants). You can specify any model available in your Ollama installation using the `-m` flag. The thesis discusses model choices and trade‑offs in more detail; see the Thesis page.

**Q: What environments are supported?**

A: Grid‑worlds defined as square ASCII maps where `.` is walkable, `X` is blocked and `G` is the goal. All rows must have the same width. The Rust core treats the world as a stateless MDP with deterministic transitions and a single goal.

**Q: What does the Rust core provide?**

A: It implements the world dynamics, homomorphism‑based abstraction (including transition and reward matrices) and an MCTS runner exposed to Python via `pyo3`. See the Rust API page for the full rustdoc.

**Q: How do I ensure reproducible runs?**

A: Prefer running inside a container on a compute cluster using the definitions under `container/`. Due to the computational cost of end‑to‑end benchmarks, it is recommended to schedule and run a single benchmark per job rather than sweeping many configurations at once.

**Q: Where can I read the thesis?**

A: The Thesis page embeds the PDF directly and also offers a download link. It contains background on abstraction, metrics and the experimental setup used here.

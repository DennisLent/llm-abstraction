# Methodology

- Abstraction: cluster-based equivalence classes (why clusters, not vectors) (Thesis).
- Extraction pipeline: prompt composition (Instruction/Context/Background/Representation/Output), querying via Ollama, self-refine, regex cleaning, validation (Thesis).
- Planning with abstractions: stateless Rust simulator; reversible mapping between abstract ↔ ground; evaluate ground/ideal/LLM agents under shared constraints (Thesis).
- Model-based metric: reward diff + Wasserstein over abstract transitions; Hausdorff-style lifting; similarity = 1/(1+d) (Thesis).
- Performance metric: MCTS rollouts over budget grid; compare agents (Thesis).
- Composite z: standardize structure & performance; z = zs − zg for global ranking (Thesis).

Bisimulation-style Metric (migrated)
To rate an LLM‑derived clustering, we compute a similarity score inspired by bisimulation metrics (Thesis). For two ground states in different clusters: (1) compare immediate rewards |R(si,a) − R(sj,a)|; (2) compare transition distributions lifted to the abstract space using a 1‑Wasserstein (EMD) distance; aggregate with a Hausdorff lift over actions. The final distance is the max over actions; similarity is 1/(1 + d). The composite z‑score evaluates an entire clustering by combining this model‑based score with planning performance from MCTS after z‑standardisation.

# Data Flow

- End-to-end: map generation → prompt assembly → LLM query → self‑refine/clean → model‑based score → select best → run agents → write outputs.
- Primary functions and modules are taken from the repository (read code references).

Stages (migrated)
1. Map generation: parse maps from `config.yml` and render PNGs.
2. Prompt assembly: `llm.prompts.generate_prompts` composes text from fragments.
3. LLM query: `llm.ollama.query_llm` collects valid responses with reprompting.
4. Parsing and validation: `llm.clean.clean_with_regex_and_validate` normalises to clusters.
5. Scoring: `llm.scoring.bisimulation_similarity` vs ideal abstraction from `core_rust.generate_mdp`.
6. Selection: choose the best scoring abstraction.
7. MCTS evaluation: `evaluation.mcts_llm_evaluation` runs ground/ideal/LLM agents and logs metrics.

```mermaid
sequenceDiagram
  participant User
  participant CLI as CLI (main.py)
  participant PB as generate_prompts
  participant LLM as query_llm (Ollama)
  participant CLEAN as clean_with_regex_and_validate
  participant SCORE as bisimulation_similarity
  participant RUN as mcts_evaluation / mcts_llm_evaluation
  participant RUST as core_rust (PyRunner, generate_mdp)

  User->>CLI: run benchmark-llm
  CLI->>PB: generate_prompts(compositions, prompts, world)
  PB-->>CLI: prompt
  CLI->>LLM: query_llm(prompt, runs, model, num_states)
  LLM-->>CLI: raw_responses
  CLI->>CLEAN: clean_with_regex_and_validate(raw_responses, num_states)
  CLEAN-->>CLI: clusters
  CLI->>RUST: generate_mdp(world)
  RUST-->>CLI: T, R, ideal_abstraction
  CLI->>SCORE: bisimulation_similarity(clusters, ideal_abstraction, T, R)
  SCORE-->>CLI: similarity
  CLI->>RUN: mcts_llm_evaluation(world, runner_configs,...)
  RUN->>RUST: PyRunner.run(sim_limit, sim_depth, c, gamma,...)
  RUST-->>RUN: results
  RUN-->>CLI: CSVs/plots in outputs/
```

# Data Flow

A full run moves through several stages:

1. **Map generation** – parse maps from `config.yml` and render PNGs.
2. **Prompt assembly** – `llm.prompts.generate_prompts` composes text from fragments.
3. **LLM query** – `llm.ollama.query_llm` sends prompts to the local model; optional self‑refinement loops until a valid clustering is extracted.
4. **Parsing and validation** – `llm.clean.clean_with_regex_and_validate` normalises the response into clusters.
5. **Scoring** – `llm.scoring.bisimulation_similarity` compares candidate clusters to the ideal abstraction.
6. **Selection** – the best scoring abstraction is chosen.
7. **MCTS evaluation** – `evaluation.mcts_llm_evaluation` runs ground, ideal and LLM agents with different budgets and logs metrics.

Outputs (maps, JSON groupings, scores and plots) are written under `outputs/`.

```mermaid
sequenceDiagram
  participant User
  participant CLI as CLI (main.py)
  participant PB as generate_prompts()
  participant LLM as Ollama LLM
  participant CLEAN as clean_with_regex_and_validate()
  participant SCORE as bisimulation_similarity()
  participant RUN as mcts_llm_evaluation()
  participant RUST as Rust Core

  User->>CLI: python main.py benchmark-llm -i 0 -m llama2
  CLI->>PB: generate_prompts(map, composition)
  PB-->>CLI: prompt
  CLI->>LLM: query_llm(prompt)
  LLM-->>CLI: raw_text
  CLI->>CLEAN: clean_with_regex_and_validate(raw_text)
  CLEAN-->>CLI: clustering
  CLI->>SCORE: bisimulation_similarity(clustering, ideal)
  SCORE-->>CLI: score
  CLI->>RUN: mcts_llm_evaluation(clustering)
  RUN->>RUST: simulate/search
  RUST-->>RUN: results
  RUN-->>CLI: logs, plots
  CLI-->>User: outputs/...
```

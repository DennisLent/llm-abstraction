# Python API

The `llm_abstraction` package contains the high‑level helpers used by the CLI along with lower‑level utilities for prompt generation and scoring.

## CLI helpers

| Function | Module | CLI command | Description |
|----------|--------|-------------|-------------|
| `preview_prompts()` | `llm_abstraction.main_functionality` | `preview-prompts` | Render prompts assembled from `config.yml` and `config_prompts.yml`. |
| `preview_maps()` | `llm_abstraction.main_functionality` | `preview-maps` | Generate map thumbnails and abstractability labels. |
| `mcts()` | `llm_abstraction.main_functionality` | `mcts` | Run baseline planners on ground and ideal abstractions. |
| `evaluate_prompt()` | `llm_abstraction.main_functionality` | `score-prompts` | Query an LLM and score returned clusterings. |
| `llm_abstraction()` | `llm_abstraction.main_functionality` | `benchmark-llm` | End‑to‑end run: prompt → score → MCTS. |
| `analysis()` | `llm_abstraction.main_functionality` | `analysis` | Summarise benchmarking results into tables and plots. |

Example:

```python
from llm_abstraction import preview_prompts, load_config

general = load_config("config.yml")
prompt_cfg = load_config("config_prompts.yml")
preview_prompts(general_config=general, prompt_config=prompt_cfg)
```

## Building prompts and querying models

`llm_abstraction.llm.prompts.generate_prompts` stitches together instructions, contexts and a world representation:

```python
from llm_abstraction.llm.prompts import generate_prompts
from llm_abstraction.utils import parse_maps, load_config

cfg = load_config("config.yml")
world = parse_maps(cfg["game"])[0]
comps = cfg["llm"]["compositions"]
prompts = generate_prompts(comps, prompt_cfg, world)
```

Send a prompt to an Ollama model and extract validated clusters:

```python
from llm_abstraction.llm.ollama import query_llm
res = query_llm(prompt=prompts[0], runs=2, model="llama2", num_states=16)
print(res["cleaned_responses"])
```

## Scoring abstractions

`llm_abstraction.llm.scoring.bisimulation_similarity` evaluates a candidate clustering against the ideal abstraction using transition and reward matrices:

```python
from core_rust import generate_mdp
from llm_abstraction.llm.scoring import bisimulation_similarity

mdp = generate_mdp(world)
score = bisimulation_similarity(candidate, ideal, mdp["T"], mdp["R"])
```

The score is in `[0,1]` and is used by `evaluate_prompt` and `llm_abstraction` to rank LLM outputs.

# API (Python)

The Python API mirrors the CLI and provides programmatic access to prompt generation, scoring, and evaluation. This section shows the most common entry points and how they connect to the Rust core.

Scoring. Import `bisimulation_similarity` from `llm_abstraction.llm` and pass a candidate clustering, the ideal clustering, and the ground‑MDP matrices. The function returns a similarity value in [0, 1], with 1 indicating identity.

```python
from llm_abstraction.llm import bisimulation_similarity
sim = bisimulation_similarity(candidate_clustering, ideal_clustering, transitions, rewards, c=0.5)
```

Prompting. Use `generate_prompts` to render full prompts from your compositions and `query_llm` to collect, reprompt, and validate abstractions. The result is a dictionary with `raw_responses` and `cleaned_responses`.

```python
from llm_abstraction.llm import generate_prompts, query_llm
prompts = generate_prompts(compositions, prompts_cfg, world)
res = query_llm(prompts[0], runs=20, model="deepseek-r1:7b", num_states=N)
```

Running agents. The `mcts_evaluation` and `mcts_llm_evaluation` helpers orchestrate full sweeps and save outputs. The example below runs ground and ideal agents for the first map in `config.yml`.

```python
from llm_abstraction.evaluation.evaluation_functions import mcts_evaluation
from llm_abstraction.utils import parse_maps
from llm_abstraction.utils.yaml import load_config

cfg = load_config("config.yml")
world = parse_maps(cfg["game"])[0]
runner_configs = [(False, None, "Ground"), (True, None, "Abstract")]

mcts_evaluation(
    simulation_limits=cfg["mcts_variables"]["simulation_limit"],
    simulation_depths=cfg["mcts_variables"]["simulation_depth"],
    world=world,
    runner_configs=runner_configs,
    folder_name="mcts",
    runs=cfg["mcts_variables"]["runs"],
    c=cfg["mcts_variables"]["c"],
    gamma=cfg["mcts_variables"]["gamma"],
    debug=cfg["mcts_variables"]["debug"],
)
```

Representations and matrices. The `core_rust` module exposes helpers to construct inputs for scoring directly from a world grid.

```python
import core_rust
reprs = core_rust.generate_representations_py(world)   # {"json": ..., "text": ..., "adj": ...}
mdp   = core_rust.generate_mdp(world)                  # {"T": T, "R": R, "abstraction": clusters}
```

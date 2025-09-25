# API (Python)

- Scoring
  - Import: `from llm_abstraction.llm import bisimulation_similarity`
  - Usage:
    - `sim = bisimulation_similarity(candidate_clustering, ideal_clustering, transitions, rewards, c=0.5)`

- Prompting
  - Import: `from llm_abstraction.llm import generate_prompts, query_llm`
  - Generate: `prompts = generate_prompts(compositions, prompts_cfg, world)`
  - Query/clean: `res = query_llm(prompt, runs=20, model="deepseek-r1:7b", num_states=N)` → dict with `raw_responses`, `cleaned_responses`.

- Running agents
  - Imports:
    - `from llm_abstraction.evaluation.evaluation_functions import mcts_evaluation, mcts_llm_evaluation`
    - `from llm_abstraction.utils import parse_maps`
  - Example:
    - ```python
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

- Representations & MDP matrices
  - Import: `import core_rust`
  - `core_rust.generate_representations_py(world)` → dict with `json`, `text`, `adj`.
  - `core_rust.generate_mdp(world)` → dict with `T`, `R`, `abstraction`.

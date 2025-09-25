# Configuration

Two YAML files configure experiments. The first, `config.yml`, specifies maps, MCTS parameters, and which prompt compositions to use. The second, `config_prompts.yml`, defines the reusable fragments that make up a prompt. The Python helper `llm_abstraction.utils.yaml.load_config` reads both files.

config.yml. The `game` section lists one or more square maps using YAML block scalars (`|`), with whitespace‑separated cells per row. The agent starts in the top‑left, and the goal `G` is at the bottom‑right. The `mcts_variables` section sets simulation limits and depths, the number of runs, the UCT exploration constant `c`, the discount factor `gamma`, and an optional `debug` flag. The `llm` section controls prompt generation: `tries` specifies how many valid responses to collect per map, and `compositions` lists the prompt compositions by id.

compositions. Each composition picks one `instruction`, one `necessary_context`, zero or more `background_contexts`, a `representation_key` (`text`, `json`, or `adj` from `core_rust.generate_representations_py`), and an `output` variant. `llm_abstraction.llm.prompts.generate_prompts` resolves these ids against `config_prompts.yml` and inserts the chosen representation rendered from the current map.

config_prompts.yml. This file defines fragments in four groups: `instruction`, `necessary_context`, `context`, and `output`. Each entry has an `id` and a `val`. When you add or remove fragments here, update the ids used under `llm.compositions` in `config.yml` accordingly.

Notes. Representation keys available to the prompt builder are `json`, `text`, and `adj`, all supplied by `core_rust.generate_representations_py`. If an id is missing or misspelled, the prompt builder raises a clear error so you can fix configuration mismatches quickly.

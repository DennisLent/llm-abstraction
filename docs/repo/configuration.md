# Configuration

- `config.yml`
  - `game`: list of square maps using YAML block scalars. Start at top-left; goal at bottom-right. Example:
    - `|` followed by rows like `. X .` per line.
  - `mcts_variables`:
    - `simulation_limit`: list of ints
    - `simulation_depth`: list of ints
    - `runs`: int
    - `c`: float (UCT exploration)
    - `gamma`: float (discount)
    - `debug`: bool
  - `llm`:
    - `tries`: number of valid responses to collect
    - `compositions`: list of prompt compositions with keys:
      - `instruction`: id in `config_prompts.yml`
      - `necessary_context`: id in `config_prompts.yml`
      - `background_contexts`: list of ids in `config_prompts.yml`
      - `representation_key`: `text` or `json` (from `core_rust.generate_representations_py`)
      - `output`: id in `config_prompts.yml`

- `config_prompts.yml`
  - `instruction`: list of `{id, val}`
  - `necessary_context`: list of `{id, val}`
  - `context`: list of `{id, val}`
  - `output`: list of `{id, val}`

- Notes
  - `llm_abstraction.llm.prompts.generate_prompts` builds prompts by id lookups and world representation.
  - Representation keys available: `json`, `text`, `adj` (see `core_rust.generate_representations_py`).
  - Composition ids must exist in the corresponding sections.

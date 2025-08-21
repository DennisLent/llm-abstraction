# Configuration Files

Two YAML files drive experiments.

## `config.yml`

| Key | Type | Description |
|-----|------|-------------|
| `game` | list of grid maps | Each map is written as ASCII with `G` goal and `X` obstacles. |
| `mcts_variables.simulation_limit` | list[int] | Number of rollouts per planning step. |
| `mcts_variables.simulation_depth` | list[int] | Depth of each rollout. |
| `mcts_variables.runs` | int | Number of evaluation runs. |
| `mcts_variables.c` | float | UCT exploration constant. |
| `mcts_variables.gamma` | float | Discount factor. |
| `mcts_variables.debug` | bool | Print MCTS internals. |
| `llm.tries` | int | Number of model attempts to harvest valid abstractions. |
| `llm.compositions` | list | Each entry selects prompt fragments (instruction, necessary_context, background_contexts, representation_key, output). |

### Example

```yaml
game:
  - |
    . . G
mcts_variables:
  simulation_limit: [32]
  simulation_depth: [32]
  runs: 10
  c: 1.4
  gamma: 0.85
  debug: false
llm:
  tries: 5
  compositions:
    - instruction: "basic1"
      necessary_context: "necessary-domain1"
      background_contexts: []
      representation_key: "text"
      output: "out1"
```

## `config_prompts.yml`

Defines reusable prompt fragments grouped by category (e.g., `instruction`, `necessary_context`, `background_contexts`, `output`). Each entry has an `id` and `val` string.

### Example

```yaml
instruction:
  - id: "basic1"
    val: "Please group these states into abstract states."
necessary_context:
  - id: "necessary-domain1"
    val: "The grid world always has the goal located in the bottom right corner."
```

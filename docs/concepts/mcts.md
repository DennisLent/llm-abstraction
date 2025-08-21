# MCTS & Abstraction

Monte Carlo Tree Search proceeds in four phases:

1. **Selection** – follow tree policy until an unexpanded node.
2. **Expansion** – add one child representing a new action.
3. **Simulation** – roll out a playout to obtain a reward.
4. **Backpropagation** – update statistics along the path.

Abstract states reduce the branching factor in both expansion and simulation because multiple ground states share one node. The planner operates on abstract identifiers while the stateless simulator translates them to concrete coordinates (Thesis).

The Rust `Runner` switches between abstract and ground actions on every turn:

```rust
// src/core/runner.rs
let action = if let Some(mapper) = &self.mapper {
    let abs_action = agent.run(current_state.clone(), debug, show_mcts);
    let abs_state = mapper.ground_state_to_abstract(&current_state);
    let (_, ground_action) =
        mapper.abstract_state_action_to_ground(&abs_state, abs_action);
    ground_action
} else {
    agent.run(current_state.clone(), debug, show_mcts)
};
```

This mapping layer lets MCTS reason over clusters without modifying the underlying environment.

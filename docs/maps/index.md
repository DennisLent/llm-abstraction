# Maps & Abstractability

Experiments use a set of hand‑specified gridworlds at sizes 3×3, 5×5, and 9×9, defined in `config.yml` under the `game` key. The top‑left tile is the start, the bottom‑right tile is the goal, and `X` marks obstacles that block movement. The Rust core treats these maps deterministically and exposes state counts and enumerations to Python.

We characterize how “abstractable” a map is with the reduction factor R = (n − k) / n, where n is the number of reachable ground states and k is the number of abstract states in the ideal abstraction derived by the Rust core. Following the thresholds in `llm_abstraction/utils/classify.py`, we label maps as “perfect abstraction” when R ≥ 0.25, “partial abstraction” when 0 < R < 0.25, and “no abstraction” when R = 0. These labels provide a quick sense of difficulty before running planners (Thesis).

Symmetry matters: layouts with symmetric obstacle patterns tend to admit higher‑quality abstractions and yield better planning gains for all agents. The `preview-maps` command writes thumbnails to `outputs/maps/<map_hash>/`, which helps spot symmetries and anticipate results.

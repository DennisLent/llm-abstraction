# Experiments & Results

- Setup: gridworlds (3×3, 5×5, 9×9); abstractability factor R and categories (none/partial/perfect); n=20 valid abstractions per config; MCTS params (Thesis).
- Flow: build prompt → extract/clean → score → select best → run agents → log outputs (Thesis).
- LLMs: Deepseek‑R1 family generally > LLaMA; size not strictly monotonic; 7B R1 often strong; structure vs planning not always correlated; composite ranking favors R1 (Thesis).
- Prompts: JSON > text overall; adding rationale helps; instruction templates matter; Tukey HSD shows significant component effects (Thesis).
- Maps: performance drops with size; symmetry helps; Deepseek more resilient on low‑structure maps; composite highlights planning gaps (Thesis).
- Failures: concentrated in certain model–prompt pairs; mid‑sized R1 variants failed more; symmetry reduces outright failures (Thesis).

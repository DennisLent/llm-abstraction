# Maps & Abstractability

Grid worlds of sizes 3×3, 5×5 and 9×9 are used. Each map hash in `outputs/maps/` includes a PNG preview and its **reduction factor** \(R = |S| / |\Phi(S)|\), the ratio between ground states and abstract clusters (Thesis). Larger grids are possible, but for big models it is best to run on a high-performance cluster.

We categorize maps by abstractability:

- `R = 1` – no useful abstraction.
- `1 < R < |S|` – partial abstraction; some symmetry.
- `R = |S|` – perfect abstraction aligning with the optimal homomorphism.

Thumbnails can be generated with:

```bash
python main.py preview-maps
```

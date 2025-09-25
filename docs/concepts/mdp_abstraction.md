# MDPs & Abstraction

An episodic grid world can be described as an MDP \((S, A, T, R, \gamma)\) where states are tile coordinates and actions move the agent. This project abstracts **states** by grouping them into clusters; actions remain unchanged. When two ground states fall into the same cluster, the planner treats them as equivalent.

Homomorphism concepts motivate these clusters: transitions from a member of a cluster should lead to clusters in the same way, and cumulative rewards should match up to a tolerance (Thesis). For small grids this resembles a lax bisimulation: if two positions behave similarly with respect to the goal and obstacles, they can be merged.

Example: in a 3×3 world with the goal at the bottom‑right, corner tiles other than the goal have symmetric behavior. A cluster \(\{(0,0), (0,2), (2,0)\}\) preserves optimal policies by mapping their transitions to equivalent abstract neighbors.

We use **cluster‑based abstractions** rather than vector embeddings to keep the simulator stateless and to retain clear semantics for each abstract state.

<div style="max-width: 420px; margin: 1rem 0;">
  <svg viewBox="0 0 120 120" width="100%" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="3 by 3 grid with goal at bottom right">
    <defs>
      <style>
        .cell { fill: #fff; stroke: #999; }
        .goal { fill: #e3f2fd; stroke: #1565c0; }
        .label { font: 12px sans-serif; fill: #333; dominant-baseline: middle; text-anchor: middle; }
      </style>
    </defs>
    <!-- Grid cells -->
    <!-- Row 0 -->
    <rect x="0"   y="0"  width="40" height="40" class="cell"/>
    <rect x="40"  y="0"  width="40" height="40" class="cell"/>
    <rect x="80"  y="0"  width="40" height="40" class="cell"/>
    <!-- Row 1 -->
    <rect x="0"   y="40" width="40" height="40" class="cell"/>
    <rect x="40"  y="40" width="40" height="40" class="cell"/>
    <rect x="80"  y="40" width="40" height="40" class="cell"/>
    <!-- Row 2 -->
    <rect x="0"   y="80" width="40" height="40" class="cell"/>
    <rect x="40"  y="80" width="40" height="40" class="cell"/>
    <rect x="80"  y="80" width="40" height="40" class="goal"/>

    <!-- Labels -->
    <text x="100" y="100" class="label">G</text>
  </svg>
  <div style="color:#555; font-size: 0.9rem; margin-top: 0.25rem;">3×3 grid; G marks the goal at (2,2). Corners other than the goal are symmetric.</div>
</div>

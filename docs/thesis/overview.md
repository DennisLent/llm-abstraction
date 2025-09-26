# Thesis Overview

This thesis explores whether large language models can induce state abstractions that are both theoretically sound and practically useful for planning in small grid‑world environments. We construct cluster‑based abstractions from model outputs, score them against an ideal abstraction using a bisimulation‑inspired metric, and test their effect on planning with Monte Carlo Tree Search (MCTS). The pipeline is fully reproducible and combines a fast Rust simulator with a Python orchestration layer for prompting, cleaning, scoring, and running agents.

The main finding is that LLMs can approximate, and in some cases match, the ideal abstraction in small, highly symmetric environments. As environments grow or lose symmetry, both structural similarity and planning utility decrease. Across model families, Deepseek‑R1 variants generally outperform LLaMA in this setting. Prompt design matters: JSON‑based map representations and output formats, combined with rationale‑style instructions, consistently lead to better abstractions. These trends appear in both the model‑based similarity metric and in the planning returns and are captured by a composite score that standardizes and combines both.

View and download

- View in your browser: [Thesis_v2_21_08_2025.pdf](../Thesis_v2_21_08_2025.pdf)

- Download the PDF: <a href="../Thesis_v2_21_08_2025.pdf" download>Thesis_v2_21_08_2025.pdf</a>

<object data="../Thesis_v2_21_08_2025.pdf#toolbar=1&navpanes=0&scrollbar=1" type="application/pdf" width="100%" height="900px">
  <p>Your browser doesn’t support embedded PDFs. You can <a href="../Thesis_v2_21_08_2025.pdf" target="_blank" rel="noopener">view it in your browser</a> or <a href="../Thesis_v2_21_08_2025.pdf" download>download the PDF</a>.</p>
</object>

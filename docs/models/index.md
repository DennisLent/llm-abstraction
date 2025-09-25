# Models Evaluated

We evaluate two model families under local inference via Ollama: LLaMA and Deepseek‑R1, each at several parameter sizes. Because experiments run on a single workstation and prioritize repeatability, we restrict the largest models to a practical ceiling (around 70B parameters on our hardware). Model identifiers passed to the CLI should match names in the Ollama library (for example, `deepseek-r1:7b` or `llama3.1:8b`).

Across the tasks in this repository, Deepseek‑R1 variants generally outperform LLaMA on the composite score that combines structural similarity and planning returns (Thesis). The effect is not strictly monotonic with size: mid‑sized models sometimes match or beat larger ones, and structured prompts narrow the gap substantially. These observations suggest that reasoning style and instruction following, coupled with JSON‑first representations, can matter more than raw parameter count.

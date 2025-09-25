# Prompt Library

Prompts in this project are built from a small set of reusable fragments that can be combined to encourage consistent, structured outputs from different models. Each prompt composition selects one instruction, one necessary context, zero or more background contexts, one representation of the map, and one output specification. Fragments live in `config_prompts.yml`, and the active compositions are listed in `config.yml` under `llm.compositions`.

Representation matters. The Rust core can produce a textual grid, a JSON encoding, and an adjacency representation of the map (`core_rust.generate_representations_py`). In our experiments (see Thesis), JSON map representations paired with explicit JSON output instructions reduce parsing errors and improve abstraction quality relative to text‑only prompts.

Example. The snippet below shows a typical JSON‑oriented composition: a role‑style instruction, a necessary domain statement, two background contexts, a JSON map representation, and an output restriction that asks for `list[list[int]]` only.

```yaml
instruction: "role1"
necessary_context: "necessary-domain2"
background_contexts: ["domain2", "test3"]
representation_key: "json"
output: "out2"
```

Under the hood, `llm_abstraction.llm.prompts.generate_prompts` resolves the ids to their text, inserts the JSON string returned by `core_rust.generate_representations_py`, and joins the pieces into a single prompt. See Repo → Configuration for the fragment schema and how to add your own.

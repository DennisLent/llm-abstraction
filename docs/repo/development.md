# Development

- Tests
  - Rust: `cargo test`
  - Python: `pytest` (CI runs with coverage)
- Linting/formatting
  - Rust: `cargo fmt --all -- --check`, `cargo clippy --all-targets --all-features -- -D warnings`
  - Python: `flake8`
- CI & Docs
  - Workflows under `.github/workflows/`:
    - `ci.yml`: lint, clippy, coverage (Rust + Python)
    - `e2e.yml`: setup + preview commands
    - `docs.yml`: build rustdoc, bundle into MkDocs, deploy Pages
- Containers
  - See `.github/workflows/container.yml` for container build/publish.
- Local docs
  - Install `mkdocs-material` and run `mkdocs serve` to preview. Mermaid is enabled via `docs/js/mermaid-init.js`.

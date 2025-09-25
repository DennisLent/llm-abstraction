# Development

The repository includes a conventional Rust + Python toolchain with CI for linting, tests, coverage, and documentation. This page lists the most useful commands and points to the workflows that encode the same steps in GitHub Actions.

Tests. Run `cargo test` for the Rust crate and `pytest` for the Python package. The CI collects coverage for both codebases and uploads it to Codecov.

Linting and formatting. For Rust, enforce style and static checks with `cargo fmt --all -- --check` and `cargo clippy --all-targets --all-features -- -D warnings`. For Python, run `flake8` to apply the rules in `.flake8`.

CI and docs. The `.github/workflows/ci.yml` job installs toolchains, runs formatters and linters, and executes both test suites with coverage. The `e2e.yml` workflow exercises the end‑to‑end entry points (`preview-prompts` and `preview-maps`). The `docs.yml` workflow builds rustdoc, copies it into `docs/rustdoc/`, and then builds and deploys the MkDocs site to GitHub Pages.

Containers. If you need container images, see `.github/workflows/container.yml` for the build and publish configuration.

Local docs. To preview documentation locally, install `mkdocs-material` and run `mkdocs serve`. Mermaid support is enabled via `docs/js/mermaid-init.js` and a small configuration in `mkdocs.yml`.

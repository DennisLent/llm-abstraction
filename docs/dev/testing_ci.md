# Testing & CI

Run unit tests for both languages:

```bash
cargo test
pytest
```

A GitHub Actions workflow builds the documentation and can be extended to run tests on pushes. The provided `docs.yml` workflow deploys MkDocs to GitHub Pages.

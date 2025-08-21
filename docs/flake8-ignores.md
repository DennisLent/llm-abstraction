# Flake8 Ignore Rationale

The project uses a large legacy code base and automatically generated
content. The following rules are disabled to keep the linter useful
while avoiding noise from known style issues.

| Code | Reason |
| ---- | ------ |
| E203 | Whitespace before punctuation, kept for compatibility with Black formatting. |
| E266 | Excess `#` in block comments from inline section markers. |
| E501 | Long lines used for clarity in tables or URLs. |
| W291/W292/W293/W391 | Trailing or final-line whitespace produced by generated files. |
| E302/E305/E303 | Nonstandard blank line counts in legacy modules. |
| E231/E221/E225/E272/E251 | Flexible spacing improves readability in mathematical expressions. |
| E117/E128 | Indentation required for embedded Rust code snippets. |
| F401/F841 | Intentional imports or variables kept for debugging. |
| F541 | Some f-strings contain braces for later formatting. |
| E261 | Inline comments don't always use two leading spaces. |
| E722/E711 | Broad exception checks retained for quick prototyping. |

These settings are documented here and referenced from the README so
contributors understand the linting trade-offs.

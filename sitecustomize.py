"""Adjust sys.path order to avoid conflicts with third-party 'py' package.

Ensures the repository root is at the end of sys.path so that built-in and
site-packages are preferred when resolving top-level modules like 'py'. This
prevents our top-level 'py/' folder (kept for test fixtures) from shadowing
pytest's dependency on the external 'py' package.
"""

import os
import sys

try:
    root = os.path.abspath(os.getcwd())
    cleaned = []
    # Remove all occurrences of the root path
    for p in list(sys.path):
        if os.path.abspath(p) == root:
            try:
                sys.path.remove(p)
            except ValueError:
                pass
        else:
            cleaned.append(p)
    # Append a single root at the end
    sys.path.append(root)
except Exception:
    # Never fail import due to path adjustments
    pass


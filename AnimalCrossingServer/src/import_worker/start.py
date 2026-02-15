"""Workspace-local start module for the import worker.

This module lives inside the `import_worker` package so editors and tooling
can find it. Call `python start_import_worker.py` from the workspace root to
run the wrapper which delegates to this module.
"""

from .main import run


def main() -> None:
    run()


if __name__ == "__main__":
    main()

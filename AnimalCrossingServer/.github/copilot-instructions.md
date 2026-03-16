# COPILOT CHAT INSTRUCTIONS — Python project

This file is applied automatically to all chat requests in this workspace.

Purpose

- Provide concise, project-level guidance so Copilot/Chat behaves consistently
  for this Python server project.

Scope

- Applies to the whole repository. Relevant files: `src/`, `test/`, `pyproject.toml`.

Project conventions

- Follow PEP 8 for layout and naming. Prefer 4-space indentation and clear
  variable names.
- Use `ruff` for formatting and for linting. Keep formatting
  automated in CI.
- Use `isort` for import ordering.

Typing and documentation

- Add type hints for public functions and methods. Prefer precise types over
  `Any` when practical.
- Do not write docstrings ever, unless explicitly requested. When requested, use
  Google or NumPy style (be consistent).

Testing

- Use `pytest` for tests in the `test/` folder. Aim for deterministic, fast
  tests with clear given/when/then structure.
- Add tests for bug fixes and non-obvious behavior. Keep unit tests isolated
  from external services.
- Use a TDD approach at all times. Always read the instructions in .github/tdd-instructions.md before writing tests.
- It is not necessary to write tests if the requested change is for moving files, creating folders or other non-behavioural changes. In these cases, simply make the change without writing tests.
- All test names must start with `test_should_` and describe the expected behavior, e.g. `test_should_return_400_for_invalid_input`.
- Every test should contain comments for given, when and then sections, even if the test is simple. If any of these sections are combined on the same line, the sections may be specified in a single comment.
- Mocks should be avoided as much as practical. Prefer custom stubs or fakes.

Dependencies and packaging

- Declare project metadata and dependencies in `pyproject.toml`. Prefer
  pinned dev dependencies in CI for reproducible builds.
- Always verify before adding new dependencies

Security and secrets

- Never add secrets, credentials, or `.env` files to the repository. Use
  environment variables or a secrets manager and document required vars in
  README or CI.

Commit and PR guidance

- Do not commit
- Do not create pull requests

When to ask clarifying questions

- If a change affects public APIs, database schema, or cross-cutting
  architecture, ask for scope, migration plans, and rollout strategy.

Forbidden actions

- Do not introduce secrets, large binaries, or break backward-compatibility
  without a migration plan and tests.
- Do not write comments. Never write comments. There is only one exception: the words "given", "when" and "then". Only ever use those words in comments. Never anything else.

When an operation must be performed in the IDE
- If a console command must be run, always make sure that the command begins with activating the python virtual environment. For every command, no exceptions.
- Prefer IDE alternatives over console commands. For example: prefer running a unittest with the testrunner over running a test with a console command

# AnimalCrossingServer — example starters

This workspace contains three small example entrypoints and a shared `features`
package. Each project has a console entry point configured in `pyproject.toml`.

Prerequisites

- Python 3.10+ recommended
- Install the package in editable mode:

```powershell
pip install -e .
```

- Install runtime deps for the API if needed:

```powershell
pip install fastapi uvicorn
```

Start the import worker

```powershell
import-worker
```

Expected output: prints a timestamp and the message from the shared feature
("features: example feature active").

Start the API (FastAPI)

```powershell
api
```

Then test the example endpoint:

```powershell
curl http://127.0.0.1:8000/feature
```

Expected result: JSON payload from the shared feature, for example:

```json
{"message": "features: example feature active"}
```

Start the automatcher

```powershell
automatcher
```

Expected output: a short sequence of fake events printed and match results,
each including the shared feature payload.

Notes

- The package-local start modules are:
  - `src/import_worker/start.py` → `import-worker` command
  - `src/api/start.py` → `api` command
  - `src/automatcher/start.py` → `automatcher` command

- Console entry points are configured in `pyproject.toml`. After installing the
  package with `pip install -e .`, you can run each project as a command from
  anywhere in your shell.

- These example entrypoints are intentionally simple; replace the bodies with
  your real scheduling, queue consumption, and API logic as needed.

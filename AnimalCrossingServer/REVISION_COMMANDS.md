# Revision Commands

Use these commands to add Alembic revisions.

## API

```bash
api-db-revision -m "your revision message"
```

## Import Event Orchestrator

```bash
import-event-orchestrator-db-revision -m "your revision message"
```

## Import Worker
```bash
import-worker-db-revision -m "your revision message"
```

## Optional: autogenerate

```bash
api-db-revision -m "your revision message" --autogenerate
import-event-orchestrator-db-revision -m "your revision message" --autogenerate
```

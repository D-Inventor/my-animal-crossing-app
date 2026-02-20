# Async Conversion Quick Reference

Use this guide when adding new routes or database operations to maintain consistency with the async conversion.

## 1. Creating a New Async Route

**Pattern:**
```python
from typing import Annotated
from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from api.db.session import get_session
from api.db.villager import Villager
from .router import router

@router.get("/my-endpoint")
async def endpoint(db: Annotated[AsyncSession, Depends(get_session)]):
    stmt = select(Villager)
    result = await db.execute(stmt)
    villagers = result.scalars().all()
    return villagers
```

**Key Points:**
- Use `async def` for route handler
- Use `Annotated[AsyncSession, Depends(get_session)]` for DB dependency
- Use `await db.execute()` for queries
- All I/O operations must use `await`

## 2. Database Operations

### Query
```python
# Single query
stmt = select(Villager).where(Villager.name == "Bob")
result = await db.execute(stmt)
villagers = result.scalars().all()

# Single item
villager = await db.execute(select(Villager).where(Villager.id == "123"))
```

### Insert/Update
```python
villager = Villager(id="123", name="Tom")
db.add(villager)
await db.commit()

# Or with rollback handling
try:
    db.add(villager)
    await db.commit()
except Exception:
    await db.rollback()
    raise
```

### Delete
```python
stmt = delete(Villager).where(Villager.id == "123")
await db.execute(stmt)
await db.commit()
```

## 3. Async Tests

**Pattern:**
```python
import pytest
from httpx import AsyncClient

from api.app import app
from api.db import Villager

@pytest.mark.asyncio
async def test_should_do_something(mariadb_session):
    # Given: fixture provides sessionmaker and connection_url
    session_local, connection_url = mariadb_session
    
    # When: interact with database
    async with session_local() as session:
        session.add(Villager(id="123", name="Bob"))
        await session.commit()
    
    # And: call API
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/villagers/by-name/Bob")
    
    # Then: assert results
    assert resp.status_code == 200
```

**Key Points:**
- Decorator: `@pytest.mark.asyncio`
- Function: `async def`
- Fixtures still provided as parameters (pytest-asyncio handles this)
- Use `async with AsyncClient(...)` for HTTP calls
- Use `async with session_local() as session:` for DB operations
- All I/O uses `await`

## 4. Tips & Common Patterns

### Context Managers
```python
# Database session
async with session_local() as session:
    await session.execute(stmt)

# HTTP client
async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
    response = await client.get("/endpoint")

# Engine cleanup
async with engine.begin() as conn:
    await conn.run_sync(Base.metadata.create_all)
```

### Error Handling
```python
try:
    result = await db.execute(stmt)
    await db.commit()
except SQLAlchemyError as e:
    await db.rollback()
    raise
finally:
    await session.close()
```

### Batch Operations
```python
# Multiple operations
async with session_local() as session:
    session.add(villager1)
    session.add(villager2)
    session.add(villager3)
    await session.commit()
```

## 5. Connection String Format

**Sync (OLD):**
```
mysql+pymysql://user:password@localhost/database
```

**Async (NEW):**
```
mysql+aiomysql://user:password@localhost/database
```

The driver suffix changes from `pymysql` to `aiomysql`.

## 6. Common Mistakes to Avoid

❌ **WRONG:** Forgetting `await` on I/O
```python
# This will hang or fail
villagers = db.execute(stmt).scalars().all()
```

✅ **RIGHT:**
```python
villagers = (await db.execute(stmt)).scalars().all()
```

---

❌ **WRONG:** Using `with` instead of `async with`
```python
with session_local() as session:
    await session.commit()
```

✅ **RIGHT:**
```python
async with session_local() as session:
    await session.commit()
```

---

❌ **WRONG:** Mixing sync and async drivers
```python
# Changed dialect but using old pymysql connections
engine = create_async_engine("mysql+pymysql://...")
```

✅ **RIGHT:**
```python
engine = create_async_engine("mysql+aiomysql://...")
```

---

❌ **WRONG:** Using `TestClient` for async routes
```python
client = TestClient(app)
response = client.get("/endpoint")
```

✅ **RIGHT:**
```python
async with AsyncClient(app=app, base_url="http://test") as client:
    response = await client.get("/endpoint")
```

## 7. When to Apply Async

✅ **Apply async conversion:**
- FastAPI route handlers (especially with DB calls)
- Database queries and operations
- External API calls (HTTP, etc.)
- File I/O operations
- Any networking operations

❌ **Skip async conversion:**
- Simple utility functions with no I/O
- Pure CPU-bound operations
- Worker processes with no I/O (unless they spawn tasks)
- Configuration loading (happens once at startup)

import json
from dataclasses import dataclass
from enum import Enum
from typing import AsyncGenerator

import httpx
import pytest
from sqlalchemy.ext.asyncio import async_sessionmaker

from import_worker.db.snapshot import Base


class HttpMethod(str, Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    DELETE = "DELETE"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"


@dataclass()
class RequestRecord:
    payload: dict[str, object] | None
    params: httpx.QueryParams


class RequestHandle:
    def __init__(self, method: HttpMethod, path: str) -> None:
        self.method = method
        self.path = path
        self._response = httpx.Response(status_code=404)
        self._calls: list[RequestRecord] = []

    def respond_with(self, *, status_code: int, json: dict[str, object]) -> None:
        self._response = httpx.Response(status_code=status_code, json=json)

    def record_call(
        self, payload: dict[str, object] | None, params: httpx.QueryParams
    ) -> None:
        self._calls.append(RequestRecord(payload=payload, params=params))

    def get_calls(self) -> int:
        return len(self._calls)

    def get_last_request(self) -> RequestRecord | None:
        if not self._calls:
            return None
        return self._calls[-1]

    def build_response(self) -> httpx.Response:
        return self._response


class ApiMock:
    def __init__(self) -> None:
        self._handles: dict[tuple[HttpMethod, str], RequestHandle] = {}

    def for_request(self, method: HttpMethod, path: str) -> RequestHandle:
        key = (method, path)
        if key not in self._handles:
            self._handles[key] = RequestHandle(method, path)
        return self._handles[key]

    def handle(self, request: httpx.Request) -> httpx.Response:
        handle = self.for_request(HttpMethod(request.method), request.url.path)
        payload = (
            json.loads(request.content.decode("utf-8")) if request.content else None
        )
        handle.record_call(payload, request.url.params)
        return handle.build_response()


@pytest.fixture()
def api() -> ApiMock:
    return ApiMock()


@pytest.fixture()
async def client(api: ApiMock) -> AsyncGenerator[httpx.AsyncClient]:
    transport = httpx.MockTransport(api.handle)
    async with httpx.AsyncClient(
        transport=transport, base_url="https://api.example.test"
    ) as http_client:
        yield http_client


@pytest.fixture
async def session_maker(mariadb_engine):
    async with mariadb_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield async_sessionmaker(bind=mariadb_engine, expire_on_commit=False)

import pytest
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session
from testcontainers.postgres import PostgresContainer

from api.features.amiibo.domain import Amiibo, AmiiboBase
from api.features.amiibo.getbyid import (
    AmiiboNotFoundError,
    GetAmiiboByIDQuery,
    GetAmiiboByIDResult,
    handle_get_amiibo_by_id,
)

postgres = PostgresContainer("postgres:16-alpine")


@pytest.fixture(scope="module", autouse=True, name="engine")
def setup(request: pytest.FixtureRequest):
    postgres.start()

    def cleanup():
        engine.dispose()
        postgres.stop()

    request.addfinalizer(cleanup)

    engine = create_engine(postgres.get_connection_url(driver="psycopg"), echo=True)

    yield engine


@pytest.fixture(scope="function", autouse=True)
def clear_data(engine: Engine):
    AmiiboBase.metadata.drop_all(engine)
    AmiiboBase.metadata.create_all(engine)


def test_gets_amiibo_by_id(engine: Engine):
    with Session(engine) as session:
        amiibo = Amiibo(id="12345", name="Test Amiibo")
        session.add(amiibo)
        session.commit()

    with Session(engine) as session:
        result = handle_get_amiibo_by_id(session, GetAmiiboByIDQuery(id="12345"))
        assert isinstance(result, GetAmiiboByIDResult)


def test_returns_not_found_for_missing_amiibo(engine: Engine):
    with Session(engine) as session:
        result = handle_get_amiibo_by_id(session, GetAmiiboByIDQuery(id="12345"))
        assert isinstance(result, AmiiboNotFoundError)

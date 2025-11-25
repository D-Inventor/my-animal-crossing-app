import pytest
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session
from testcontainers.postgres import PostgresContainer

from api.features.characters.domain import (
    Character,
    CharacterAmiiboAssociation,
    CharacterBase,
    CharacterGender,
    CharacterPersonality,
    CharacterSpecies,
)
from api.features.characters.getbyamiiboid import (
    CharacterNotFoundError,
    GetCharacterByAmiiboIDQuery,
    GetCharacterByAmiiboIDResult,
    handle_get_character_by_amiibo_id,
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
    CharacterBase.metadata.drop_all(engine)
    CharacterBase.metadata.create_all(engine)


def test_gets_character_by_amiibo_id(engine: Engine):
    with Session(engine) as session:
        session.add(
            Character(
                id=1,
                external_id="ext-123",
                name="Test Character",
                species=CharacterSpecies.DOG,
                personality=CharacterPersonality.LAZY,
                gender=CharacterGender.MALE,
                hobby="Fishing",
            )
        )
        session.add(CharacterAmiiboAssociation(character_id=1, amiibo_id="amiibo-123"))
        session.commit()

    with Session(engine) as session:
        result = handle_get_character_by_amiibo_id(
            session, GetCharacterByAmiiboIDQuery(amiibo_id="amiibo-123")
        )
        assert isinstance(result, GetCharacterByAmiiboIDResult)


def test_returns_not_found_for_missing_character(engine: Engine):
    with Session(engine) as session:
        result = handle_get_character_by_amiibo_id(
            session, GetCharacterByAmiiboIDQuery(amiibo_id="nonexistent-amiibo")
        )
        assert isinstance(result, CharacterNotFoundError)

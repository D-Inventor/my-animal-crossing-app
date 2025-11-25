from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from .config import settings
from .features.amiibo.domain import AmiiboBase
from .features.characters.domain import CharacterBase

engine = create_engine(settings.connectionstring, echo=True)

# NOTE: this has to go later: we don't just want to create
#    the whole database every time we start the application
AmiiboBase.metadata.create_all(engine)
CharacterBase.metadata.create_all(engine)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db_session() -> Generator[Session]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

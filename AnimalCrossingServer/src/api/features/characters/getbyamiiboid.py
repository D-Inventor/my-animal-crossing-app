from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session

from .domain import (
    Character,
    CharacterAmiiboAssociation,
    CharacterGender,
    CharacterPersonality,
    CharacterSpecies,
)


@dataclass(frozen=True)
class GetCharacterByAmiiboIDQuery:
    amiibo_id: str


def handle_get_character_by_amiibo_id(
    session: Session, query: GetCharacterByAmiiboIDQuery
) -> GetCharacterByAmiiboIDResult | CharacterNotFoundError:
    subquery = select(CharacterAmiiboAssociation.character_id).where(
        CharacterAmiiboAssociation.amiibo_id == query.amiibo_id
    )
    main_query = select(Character).where(Character.id.in_(subquery))
    character = session.execute(main_query).scalar_one_or_none()
    return (
        GetCharacterByAmiiboIDResult(
            id=character.id,
            external_id=character.external_id,
            name=character.name,
            gender=character.gender,
            personality=character.personality,
            hobby=character.hobby,
            species=character.species,
            image_url=character.image_url,
        )
        if character
        else CharacterNotFoundError()
    )


@dataclass(frozen=True)
class GetCharacterByAmiiboIDResult:
    id: int
    external_id: str
    name: str
    gender: CharacterGender
    personality: CharacterPersonality
    hobby: str
    species: CharacterSpecies
    image_url: str


@dataclass(frozen=True)
class CharacterNotFoundError:
    pass

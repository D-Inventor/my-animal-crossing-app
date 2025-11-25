from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ...database import get_db_session
from .domain import CharacterGender, CharacterPersonality, CharacterSpecies
from .getbyamiiboid import (
    GetCharacterByAmiiboIDQuery,
    GetCharacterByAmiiboIDResult,
    handle_get_character_by_amiibo_id,
)

router = APIRouter(
    prefix="/api/characters",
    tags=["characters"],
)


class GetCharacterByAmiiboIDApiResponse(BaseModel):
    id: int
    external_id: str
    name: str
    species: CharacterSpecies
    personality: CharacterPersonality
    gender: CharacterGender
    hobby: str
    image_url: str


@router.get("")
def get_character_by_amiibo_id(
    amiibo_id: str, session: Annotated[Session, Depends(get_db_session)]
) -> GetCharacterByAmiiboIDApiResponse:
    result = handle_get_character_by_amiibo_id(
        session, GetCharacterByAmiiboIDQuery(amiibo_id=amiibo_id)
    )

    if isinstance(result, GetCharacterByAmiiboIDResult):
        return GetCharacterByAmiiboIDApiResponse(
            id=result.id,
            external_id=result.external_id,
            name=result.name,
            species=result.species,
            personality=result.personality,
            gender=result.gender,
            hobby=result.hobby,
            image_url=result.image_url,
        )
    else:
        raise HTTPException(status_code=404, detail="Character not found")

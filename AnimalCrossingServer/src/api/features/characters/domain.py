import enum

from sqlalchemy import Enum, ForeignKey, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class CharacterBase(DeclarativeBase):
    pass


class CharacterPersonality(enum.Enum):
    LAZY = "Lazy"
    JOCK = "Jock"
    CRANKY = "Cranky"
    SMUG = "Smug"
    NORMAL = "Normal"
    PEPPY = "Peppy"
    SNOOTY = "Snooty"
    BIG_SISTER = "Big Sister"


class CharacterGender(enum.Enum):
    MALE = "Male"
    FEMALE = "Female"


class CharacterSpecies(enum.Enum):
    ALLIGATOR = "alligator"
    ANTEATER = "anteater"
    BEAR = "bear"
    BEAR_CUB = "bear cub"
    BIRD = "bird"
    BULL = "bull"
    CAT = "cat"
    CUB = "cub"
    CHICKEN = "chicken"
    COW = "cow"
    DEER = "deer"
    DOG = "dog"
    DUCK = "duck"
    EAGLE = "eagle"
    ELEPHANT = "elephant"
    FROG = "frog"
    GOAT = "goat"
    GORILLA = "gorilla"
    HAMSTER = "hamster"
    HIPPO = "hippo"
    HORSE = "horse"
    KOALA = "koala"
    KANGAROO = "kangaroo"
    LION = "lion"
    MONKEY = "monkey"
    MOUSE = "mouse"
    OCTOPUS = "octopus"
    OSTRICH = "ostrich"
    PENGUIN = "penguin"
    PIG = "pig"
    RABBIT = "rabbit"
    RHINO = "rhino"
    RHINOCEROS = "rhinoceros"
    SHEEP = "sheep"
    SQUIRREL = "squirrel"
    TIGER = "tiger"
    WOLF = "wolf"


class Character(CharacterBase):
    __tablename__ = "characters"

    # Define your columns here
    id: Mapped[int] = mapped_column(primary_key=True)
    external_id: Mapped[str] = mapped_column(String(50), unique=True)
    name: Mapped[str] = mapped_column(String(100))
    personality: Mapped[CharacterPersonality] = mapped_column(
        Enum(CharacterPersonality)
    )
    gender: Mapped[CharacterGender] = mapped_column(Enum(CharacterGender))
    hobby: Mapped[str] = mapped_column(String(50))
    species: Mapped[CharacterSpecies] = mapped_column(Enum(CharacterSpecies))
    image_url: Mapped[str] = mapped_column(String(256))

    def __repr__(self) -> str:
        return f"Character(id={self.id!r}, name={self.name!r})"


class CharacterAmiiboAssociation(CharacterBase):
    __tablename__ = "character_amiibo_associations"

    character_id: Mapped[int] = mapped_column(
        ForeignKey("characters.id", ondelete="CASCADE"), primary_key=True
    )
    amiibo_id: Mapped[str] = mapped_column(String(16), primary_key=True)

    def __repr__(self) -> str:
        return f"CharacterAmiiboAssociation(character_id={self.character_id!r}, amiibo_id={self.amiibo_id!r})"

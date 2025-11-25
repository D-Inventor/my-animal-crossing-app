from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class AmiiboBase(DeclarativeBase):
    pass


class Amiibo(AmiiboBase):
    __tablename__ = "amiibos"

    id: Mapped[str] = mapped_column(String(16), primary_key=True)
    name: Mapped[str] = mapped_column(String(100))

    def __repr__(self) -> str:
        return f"Amiibo(id={self.id!r}, name={self.name!r})"

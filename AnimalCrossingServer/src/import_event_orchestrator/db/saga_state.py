from enum import Enum
from typing import Self
from uuid import UUID, uuid4

from sqlalchemy import JSON
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class SagaStatus(str, Enum):
    STARTED = "started"
    COMPLETED = "completed"
    FAILED = "failed"
    COMPENSATING = "compensating"


class SagaState(Base):
    __tablename__ = "saga_state"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    state: Mapped[SagaStatus] = mapped_column(
        SQLEnum(
            SagaStatus,
            name="sagastatus",
            values_callable=lambda enum_cls: [member.value for member in enum_cls],
        ),
        nullable=False,
        default=SagaStatus.STARTED,
    )
    completed_steps: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=[])
    data: Mapped[dict] = mapped_column(JSON, nullable=False, default={})

    @classmethod
    def create(cls, id: UUID | None = None) -> Self:
        return cls(
            id=id or uuid4(),
            state=SagaStatus.STARTED,
            completed_steps=[],
            data={},
        )

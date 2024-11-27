from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.database import Win


class User(Base):
    id: Mapped[str] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(nullable=True)
    wins_relationship: Mapped[list["Win"]] = relationship(back_populates="user_relationship")

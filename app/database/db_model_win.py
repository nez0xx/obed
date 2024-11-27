from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.database import User


class Win(Base):
    contest_id: Mapped[int] = mapped_column(ForeignKey("contests.id"))
    type: Mapped[str]
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"))
    user_relationship: Mapped["User"] = relationship(back_populates="wins_relationship",
                                                     )

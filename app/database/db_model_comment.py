from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class Comment(Base):
    contest_id: Mapped[int] = mapped_column(ForeignKey("contests.id"))
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"))



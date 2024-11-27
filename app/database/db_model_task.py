from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class Task(Base):
    contest_id: Mapped[int] = mapped_column(ForeignKey("contests.id"))
    id: Mapped[int] = mapped_column(primary_key=True)



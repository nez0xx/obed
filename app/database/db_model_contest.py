from datetime import datetime

from sqlalchemy.orm import Mapped, declared_attr, mapped_column
from app.database import Base


class Contest(Base):

    @declared_attr.directive
    def __tablename__(cls):
        return "contests"

    post_id: Mapped[int]
    start_time: Mapped[datetime]
    end_time: Mapped[datetime]
    completed: Mapped[bool] = mapped_column(default=False)

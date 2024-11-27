from typing import Any


class DetailedException(Exception):
    def __init__(
        self,
        detail: str | None = None
    ) -> None:
        if detail is None:
            detail = "None"
        self.detail = detail

    def __str__(self) -> str:
        return self.detail

    def __repr__(self) -> str:
        class_name = self.__class__.__name__
        return f"{class_name}(detail={self.detail!r})"


class Conflict(DetailedException):
    DETAIL = "Conflict"

    def __init__(self, detail: str | None = None) -> None:
        if detail is None:
            detail = self.DETAIL
        super().__init__(detail=detail)

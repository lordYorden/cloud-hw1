from typing import TypeVar, Generic
from fastapi import Query
from fastapi_pagination import Page, Params, set_page
from fastapi_pagination.bases import RawParams
from pydantic import Field


class ZeroBasedParams(Params):
    """Pagination parameters with 0-indexed page numbers."""
    page: int = Query(0, ge=0, description="Page number (0-indexed)")

    def to_raw_params(self) -> RawParams:
        return RawParams(
            limit=self.size if self.size is not None else None,
            offset=self.page * self.size if self.size is not None else None,
        )


T = TypeVar("T")


class ZeroBasedPage(Page[T], Generic[T]):
    """Page model with 0-indexed page numbers."""
    page: int = Field(ge=0)

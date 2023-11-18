from typing import Any, TypeVar
from .types import DataclassInstance

T = TypeVar("T", bound=DataclassInstance)

def to_document(obj: T, /) -> dict[str, Any]:
    pass

def _to_document_helper(obj: Any, /) -> Any:
    pass

def from_document(cls: type[T], /, data: dict[str, Any]) -> T:
    pass

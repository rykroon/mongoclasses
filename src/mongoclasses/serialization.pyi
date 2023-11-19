from typing import Any, TypeVar
from .types import DataclassInstance

T = TypeVar("T", bound=DataclassInstance)

def to_document(obj: T, /) -> dict[str, Any]:
    pass

def _convert_value(value: Any, /) -> Any:
    pass

def from_document(cls: type[T], /, data: dict[str, Any]) -> T:
    pass

def resolve_type(t: type) -> type | list[type]:
    pass

def is_union(t: type) -> bool:
    pass

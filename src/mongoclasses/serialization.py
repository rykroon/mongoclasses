from dataclasses import is_dataclass
from functools import lru_cache
from typing import Any, Dict, Type, TypeVar

from pydantic import TypeAdapter
from pydantic.dataclasses import dataclass


T = TypeVar("T")


@lru_cache
def _get_type_adapter(t: Type, /) -> TypeAdapter:
    if not is_dataclass(t):
        raise TypeError("Not a dataclass.")

    is_pydantic_dataclass = any("pydantic" in attr for attr in t.__dict__.keys())

    if not is_pydantic_dataclass:
        t = dataclass(config=dict(arbitrary_types_allowed=True))(t)

    return TypeAdapter(t)


def to_document(obj: Any, /) -> Dict[str, Any]:
    adapter = _get_type_adapter(type(obj))
    return adapter.dump_python(obj)


def from_document(cls: Type[T], data: Dict[str, Any]) -> T:
    adapter = _get_type_adapter(cls)
    return adapter.validate_python(data)

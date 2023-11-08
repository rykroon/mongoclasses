from dataclasses import is_dataclass, fields, _FIELD_CLASSVAR
from functools import lru_cache
import inspect
from typing import Any, Type

from pydantic.dataclasses import is_pydantic_dataclass


def is_mongoclass(obj: Any, /) -> bool:
    """
    Returns True if the obj is a mongoclass or an instance of
    a mongoclass.
    """
    if not inspect.isclass(obj):
        obj = type(obj)
    return _is_mongoclass_type(obj)


def _is_mongoclass_instance(obj: Any, /) -> bool:
    """
    Returns True if the obj is an instance of a mongoclass.
    """
    return _is_mongoclass_type(type(obj))


@lru_cache
def _is_mongoclass_type(t: Type, /) -> bool:
    if not is_dataclass(t):
        return False

    dataclass_fields = getattr(t, "__dataclass_fields__")
    if "collection" not in dataclass_fields:
        return False

    if dataclass_fields["collection"]._field_type is not _FIELD_CLASSVAR:
        return False

    if "_id" in dataclass_fields:
        return True

    # If an _id field is not present, check if the dataclass is a pydantic dataclass
    # and check if it has a field with an alias of "_id".
    if not is_pydantic_dataclass(t):
        return False

    for field in t.__pydantic_fields__.values():
        if field.alias == "_id":
            return True

    return False

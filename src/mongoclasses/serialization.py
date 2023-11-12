from collections.abc import Mapping
from dataclasses import is_dataclass, fields
from typing import Any, Dict, Type, TYPE_CHECKING

from .types import is_dataclass_instance, is_dataclass_type
from .utils import get_field_name

if TYPE_CHECKING:
    from _typeshed import DataclassInstance


def to_document(obj: "DataclassInstance", /) -> Dict[str, Any]:
    if is_dataclass_instance(obj):
        field_names = (get_field_name(field) for field in fields(obj))
        return {
            field_name: to_document(getattr(obj, field_name))
            for field_name in field_names
        }

    if isinstance(obj, (list, tuple, set)):
        return [to_document(item) for item in obj]

    if isinstance(obj, Mapping):
        return {k: to_document(v) for k, v in obj.items()}

    return obj


def from_document(
    cls: Type["DataclassInstance"], /, data: Dict[str, Any]
) -> "DataclassInstance":
    """
    Attempts to create a dataclass instance from a dictionary.
    """
    if not is_dataclass_type(cls):
        raise TypeError("Object must be a dataclass type.")

    init_values = {}
    non_init_values = {}
    for field in fields(cls):
        db_field = get_field_name(field)
        if db_field not in data:
            continue

        value = data[db_field]

        if isinstance(value, Mapping) and is_dataclass(field.type):
            value = from_document(field.type, value)

        if field.init:
            init_values[field.name] = value
        else:
            non_init_values[field.name] = value

    obj = cls(**init_values)
    for field_name, value in non_init_values.items():
        setattr(obj, field_name, value)

    return obj

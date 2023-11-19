from collections.abc import Mapping
from dataclasses import is_dataclass, fields
from typing import Union
from typing_extensions import get_args, get_origin, Annotated

from .utils import get_field_name, is_dataclass_instance, is_dataclass_type


def to_document(obj, /):
    """
    Converts a dataclass instance to a dictionary.
    """
    if not is_dataclass_instance(obj):
        raise TypeError("Object must be a dataclass instance.")

    field_names = (get_field_name(field) for field in fields(obj))
    return {
        field_name: _to_document_inner(getattr(obj, field_name))
        for field_name in field_names
    }


def _to_document_inner(value, /):
    if is_dataclass_instance(value):
        return to_document(value)

    if isinstance(value, (list, tuple)):
        return [_to_document_inner(item) for item in value]

    if isinstance(value, Mapping):
        return {k: _to_document_inner(v) for k, v in value.items()}

    return value


def from_document(cls, /, data):
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


def resolve_type(t):
    origin = get_origin(t)
    if origin is None:
        return t

    if origin is Annotated:
        return resolve_type(get_args(t)[0])

    if is_union(t):
        return tuple([resolve_type(arg) for arg in get_args(t)])

    return origin


def is_union(t):
    if get_origin(t) is Union:
        return True

    try:
        # UnionType was introduced in python 3.10
        from types import UnionType

        return isinstance(t, UnionType)

    except ImportError:
        return False

from collections.abc import Mapping
from dataclasses import is_dataclass, fields

import dacite

from .utils import get_field_name


def to_document(obj, /):
    """
    Converts a dataclass instance to a dictionary.
    """
    if not is_dataclass(obj):
        raise TypeError("Object must be a dataclass instance.")

    field_names = (get_field_name(field) for field in fields(obj))
    return {
        field_name: _to_document_inner(getattr(obj, field_name))
        for field_name in field_names
    }


def _to_document_inner(value, /):
    if is_dataclass(value):
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
    if not is_dataclass(cls):
        raise TypeError("Object must be a dataclass type.")

    return dacite.from_dict(cls, data, config=dacite.Config(check_types=False))

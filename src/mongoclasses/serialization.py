from collections.abc import Mapping
from dataclasses import is_dataclass, fields, MISSING
import inspect


def to_document(obj, /):
    result = {}
    for field in fields(obj):
        db_field = field.metadata.get("mongoclasses", {}).get("db_field", field.name)
        value = _to_document_helper(getattr(obj, field.name))
        result[db_field] = value
    return result


def _to_document_helper(value, /):
    if is_dataclass(value):
        return to_document(value)
    
    if isinstance(value, (list, tuple)):
        return [_to_document_helper(i) for i in value]

    if isinstance(value, Mapping):
        return {k: _to_document_helper(v) for k, v in value.items()}

    return value


def from_document(cls, /, data):
    """
    Attempts to create a dataclass instance from a dictionary.
    """
    if not inspect.isclass(cls):
        raise TypeError("Object must be a dataclass type.")

    if not is_dataclass(cls):
        raise TypeError("Object must be a dataclass type.")

    init_values = {}
    non_init_values = {}
    for field in fields(cls):
        db_field = field.metadata.get("mongoclasses", {}).get("db_field", field.name)
        if db_field in data:
            value = data[db_field]
        else:
            if field.default is not MISSING:
                value = field.default
            elif field.default_factory is not MISSING:
                value = field.default_factory()
            else:
                value = MISSING 

        if isinstance(value, Mapping) and is_dataclass(field.type):
            value = from_document(field.type, value)

        if field.init:
            init_values[field.name] = value
        else:
            non_init_values[field.name] = value

    obj = cls(**init_values)
    for field, value in non_init_values.items():
        setattr(obj, field, value)

    return obj

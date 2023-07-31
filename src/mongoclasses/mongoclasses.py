from dataclasses import is_dataclass, fields, MISSING, _FIELD_CLASSVAR, _FIELD
from functools import lru_cache
import inspect


def to_document(obj, /, include=None):
    result = {}
    for field in fields(obj):
        if include is not None and field.name not in include:
            continue

        value = getattr(obj, field.name)
        if is_dataclass(value):
            value = to_document(value)

        db_field = field.metadata.get("mongoclasses", {}).get("db_field", field.name)
        result[db_field] = value
    return result


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

        if isinstance(value, dict) and is_dataclass(field.type):
            value = from_document(field.type, value)

        if field.init:
            init_values[field.name] = value
        else:
            non_init_values[field.name] = value

    obj = cls(**init_values)
    for field, value in non_init_values.items():
        setattr(obj, field, value)

    return obj


def is_mongoclass(obj, /):
    """
    Returns True if the obj is a mongoclass or an instance of
    a mongoclass.
    """
    if not inspect.isclass(obj):
        obj = type(obj)
    return _is_mongoclass_type(obj)


def _is_mongoclass_instance(obj, /):
    """
    Returns True if the obj is an instance of a mongoclass.
    """
    return _is_mongoclass_type(type(obj))


@lru_cache
def _is_mongoclass_type(t, /):
    if not is_dataclass(t):
        return False

    dataclass_fields = getattr(t, "__dataclass_fields__")
    if "collection" not in dataclass_fields:
        return False

    if dataclass_fields["collection"]._field_type is not _FIELD_CLASSVAR:
        return False

    for field in fields(t):
        db_field = field.metadata.get("mongoclasses", {}).get("db_field", field.name)
        if db_field == "_id":
            return True

    return False

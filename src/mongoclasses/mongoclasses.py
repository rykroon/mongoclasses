
from dataclasses import is_dataclass, _FIELD_CLASSVAR, _FIELD
import inspect


def fromdict(cls, /, data):
    """
    Attempts to create a dataclass instance from a dictionary.
    """
    if not is_dataclass(cls):
        raise TypeError("Object must be a dataclass type.")

    if not inspect.isclass(cls):
        raise TypeError("Object must be a dataclass type.")

    init_values = {}
    non_init_values = []
    for field in cls.__dataclass_fields__.values():
        if field._field_type is _FIELD_CLASSVAR:
            continue

        if field.name not in data:
            continue

        if field.init:
            init_values[field.name] = data[field.name]
        else:
            non_init_values.append(((field.name, data[field.name])))

    obj = cls(**init_values)
    for field, value in non_init_values:
        setattr(obj, field, value)

    return obj


def is_mongoclass(obj, /):
    """
    Returns True if the obj is a mongoclass or an instance of
    a mongoclass.
    """
    if not is_dataclass(obj):
        return False

    dataclass_fields = getattr(obj, "__dataclass_fields__")
    if "_id" not in dataclass_fields:
        return False

    if dataclass_fields["_id"]._field_type is not _FIELD:
        return False

    if "collection" not in dataclass_fields:
        return False

    if dataclass_fields["collection"]._field_type is not _FIELD_CLASSVAR:
        return False

    return True


def _is_mongoclass_type(obj, /):
    if not inspect.isclass(obj):
        return False
    return is_mongoclass(obj)


def _is_mongoclass_instance(obj, /):
    """
    Returns True if the obj is an instance of a mongoclass.
    """
    return is_mongoclass(type(obj))
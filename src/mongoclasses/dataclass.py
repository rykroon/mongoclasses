from dataclasses import is_dataclass, MISSING, _FIELD, _FIELD_CLASSVAR
from functools import lru_cache
import inspect


def fromdict(cls, /, data):
    """
    Creates a dataclass instance from a dictionary.

    Parameters:
        data: A dictionary containing the data to create the dataclass.

    Returns:
        A dataclass instance.
    """
    init_values = {}
    non_init_values = {}

    for field in cls.__dataclass_fields__.values():
        if field._field_type is _FIELD_CLASSVAR:
            continue

        if field.name in data:
            value = data[field.name]

        elif field.default is not MISSING:
            value = field.default
            
        elif field.default_factory is not MISSING:
            value = field.default_factory()

        else:
             continue

        if is_dataclass(field.type):
            value = fromdict(field.type, value)

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
    Returns True if the object is a mongoclass type or instance else False.

    Parameters:
        obj: Any object.
    
    Returns:
        True if the object is a mongoclass type or instance.
    """
    if not inspect.isclass(obj):
        obj = type(obj)
    return _is_mongoclass_type(obj)


def _is_mongoclass_instance(obj, /):
    return _is_mongoclass_type(type(obj))


@lru_cache
def _is_mongoclass_type(obj, /):
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

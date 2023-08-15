from dataclasses import is_dataclass, fields, _FIELD_CLASSVAR
from functools import lru_cache
import inspect


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

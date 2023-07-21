from dataclasses import is_dataclass, _FIELD_CLASSVAR
from functools import lru_cache
import inspect

from .converters import register_db_name_overrides
from .utils import _get_id_field


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
def _is_mongoclass_type(type_, /):
    if not is_dataclass(type_):
        return False

    dataclass_fields = getattr(type_, "__dataclass_fields__")
    if "collection" not in dataclass_fields:
        return False

    if dataclass_fields["collection"]._field_type is not _FIELD_CLASSVAR:
        return False

    if _get_id_field(type_) is None:
        return False

    register_db_name_overrides(type_)
    return True

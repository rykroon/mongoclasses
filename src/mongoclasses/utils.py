from dataclasses import dataclass, fields, is_dataclass, _FIELD_CLASSVAR
import inspect
from typing import Any, Optional, Union
from typing_extensions import get_args, get_origin, Annotated


@dataclass(frozen=True)
class FieldInfo:
    db_field: Optional[str] = None
    unique: bool = False
    # db_index: bool = False
    # required: bool = False


def get_field_info(field):
    if get_origin(field.type) is not Annotated:
        return None

    for annotation in field.type.__metadata__:
        if isinstance(annotation, FieldInfo):
            return annotation

    return None


def get_field_name(field):
    field_info = get_field_info(field)
    if field_info is None or field_info.db_field is None:
        return field.name

    return field_info.db_field


def get_id_field(cls):
    for field in fields(cls):
        if get_field_name(field) == "_id":
            return field
    raise TypeError(f"Object {cls} has no _id field")


def set_id(obj, id):
    field = get_id_field(type(obj))
    setattr(obj, field.name, id)


def get_id(obj) -> Any:
    field = get_id_field(type(obj))
    return getattr(obj, field.name)


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


def is_dataclass_type(obj, /):
    if not is_dataclass(obj):
        return False

    return inspect.isclass(obj)


def is_dataclass_instance(obj, /):
    return is_dataclass_type(type(obj))


def is_mongoclass(obj, /):
    if not is_dataclass(obj):
        return False

    if "collection" not in obj.__dataclass_fields__:
        return False

    if obj.__dataclass_fields__["collection"]._field_type is not _FIELD_CLASSVAR:
        return False

    if "_id" in obj.__dataclass_fields__:
        return True

    try:
        get_id_field(obj)
    except TypeError:
        return False
    else:
        return True


def is_mongoclass_type(obj, /):
    if not is_mongoclass(obj):
        return False

    return inspect.isclass(obj)


def is_mongoclass_instance(obj, /):
    return is_mongoclass_type(type(obj))

from dataclasses import dataclass, fields, is_dataclass, _FIELD_CLASSVAR
import inspect
from typing import Optional
from typing_extensions import get_origin, Annotated


@dataclass(frozen=True)
class FieldMeta:
    db_field: Optional[str] = None
    unique: bool = False


def get_field_meta(field):
    if get_origin(field.type) is not Annotated:
        return None

    for annotation in field.type.__metadata__:
        if isinstance(annotation, FieldMeta):
            return annotation

    return None


def get_field_name(field):
    field_meta = get_field_meta(field)

    if field_meta is not None and field_meta.db_field is not None:
        return field_meta.db_field

    return field.name


def get_id_field(cls, /):
    for field in fields(cls):
        if get_field_name(field) == "_id":
            return field
    raise TypeError(f"Object {cls} has no _id field")


def set_id(obj, /, id):
    field = get_id_field(type(obj))
    setattr(obj, field.name, id)


def get_id(obj, /):
    field = get_id_field(type(obj))
    return getattr(obj, field.name)


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

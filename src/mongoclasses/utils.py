from dataclasses import dataclass, fields, Field
from typing import Any, List, Optional, Type, Union
from typing_extensions import get_args, get_origin, Annotated


@dataclass(frozen=True)
class FieldInfo:
    db_field: Optional[str] = None
    unique: bool = False
    # db_index: bool = False
    # required: bool = False


def get_field_info(field: Field) -> Optional[FieldInfo]:
    if get_origin(field.type) is not Annotated:
        return None

    for annotation in field.type.__metadata__:
        if isinstance(annotation, FieldInfo):
            return annotation

    return None


def get_field_name(field: Field) -> str:
    field_info = get_field_info(field)
    if field_info is None or field_info.db_field is None:
        return field.name

    return field_info.db_field


def get_id_field(cls: Type) -> Field:
    for field in fields(cls):
        if get_field_name(field) == "_id":
            return field
    raise TypeError(f"Object {cls} has no _id field")


def set_id(obj, id: Any):
    field = get_id_field(type(obj))
    setattr(obj, field.name, id)


def get_id(obj):
    field = get_id_field(type(obj))
    return getattr(obj, field.name)


def resolve_type(t: Type) -> Union[Type, List[Type]]:
    origin = get_origin(t)
    if origin is None:
        return t

    if origin is Annotated:
        return resolve_type(get_args(t)[0])

    if is_union(t):
        return tuple([resolve_type(arg) for arg in get_args(t)])

    return origin


def is_union(t: Type) -> bool:
    if get_origin(t) is Union:
        return True
    
    try:
        # UnionType was introduced in python 3.10
        from types import UnionType
        return isinstance(t, UnionType)

    except ImportError:
        return False

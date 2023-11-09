from dataclasses import dataclass, Field
from typing import List, Optional, Type, Union
from types import UnionType
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


def get_field_name(field: Field):
    field_info = get_field_info(field)
    return field.name if field_info is None else field_info.db_field


def resolve_type(t: Type) -> Union[Type, List[Type]]:
    origin = get_origin(t)
    if origin is None:
        return t

    if origin is Annotated:
        return resolve_type(get_args(t)[0])

    if origin is Union or origin is UnionType:
        return tuple([resolve_type(arg) for arg in get_args(t)])

    return origin

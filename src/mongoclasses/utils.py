from dataclasses import dataclass, fields, is_dataclass, Field, _FIELD_CLASSVAR
import inspect
from typing import Any, List, Optional, Type, Union
from typing_extensions import get_args, get_origin, Annotated, TypeGuard

from .types import DataclassInstance, MongoclassInstance


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


def get_id_field(cls: Type[DataclassInstance]) -> Field:
    for field in fields(cls):
        if get_field_name(field) == "_id":
            return field
    raise TypeError(f"Object {cls} has no _id field")


def set_id(obj: MongoclassInstance, id: Any) -> None:
    field = get_id_field(type(obj))
    setattr(obj, field.name, id)


def get_id(obj: MongoclassInstance) -> Any:
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


def is_dataclass_type(obj: Any) -> TypeGuard[Type[DataclassInstance]]:
    if not is_dataclass(obj):
        return False

    return inspect.isclass(obj)


def is_dataclass_instance(obj: Any) -> TypeGuard[DataclassInstance]:
    return is_dataclass_type(type(obj))


def is_mongoclass(
    obj: Any,
) -> TypeGuard[Union[MongoclassInstance, Type[MongoclassInstance]]]:
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


def is_mongoclass_type(obj: Any) -> TypeGuard[Type[MongoclassInstance]]:
    if not is_mongoclass(obj):
        return False

    return inspect.isclass(obj)


def is_mongoclass_instance(obj: Any) -> TypeGuard[MongoclassInstance]:
    return is_mongoclass_type(type(obj))

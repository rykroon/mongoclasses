from dataclasses import is_dataclass, _FIELD_CLASSVAR
import inspect
from typing import Any, ClassVar, Type, Union, TYPE_CHECKING
from typing_extensions import TypeGuard

from pymongo.collection import Collection
from motor.motor_asyncio import AsyncIOMotorCollection

from .utils import get_id_field


if TYPE_CHECKING:
    from _typeshed import DataclassInstance

    class MongoclassInstance(DataclassInstance):
        collection: ClassVar[Union[Collection, AsyncIOMotorCollection]]


def is_dataclass_type(obj: Any) -> TypeGuard[Type["DataclassInstance"]]:
    if not is_dataclass(obj):
        return False

    return inspect.isclass(obj)


def is_dataclass_instance(obj: Any) -> TypeGuard["DataclassInstance"]:
    return is_dataclass_type(type(obj))


def is_mongoclass(
    obj: Any,
) -> TypeGuard[Union["MongoclassInstance", Type["MongoclassInstance"]]]:
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


def is_mongoclass_type(obj: Any) -> TypeGuard[Type["MongoclassInstance"]]:
    if not is_mongoclass(obj):
        return False

    return inspect.isclass(obj)


def is_mongoclass_instance(obj: Any) -> TypeGuard["MongoclassInstance"]:
    return is_mongoclass_type(type(obj))

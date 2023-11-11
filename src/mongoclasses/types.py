from dataclasses import fields, is_dataclass, Field, _DataclassParams, _FIELD_CLASSVAR
import inspect
from typing import Any, Protocol, Type, Union
from typing_extensions import TypeGuard

from pymongo.collection import Collection
from motor.motor_asyncio import AsyncIOMotorCollection

from .utils import get_field_name


class Dataclass(Protocol):
    __dataclass_fields__: dict[str, Field]
    __dataclass_params__: _DataclassParams


class Mongoclass(Dataclass):
    collection: Union[Collection, AsyncIOMotorCollection]


def is_dataclass_type(obj: Any) -> TypeGuard[Type[Dataclass]]:
    if not is_dataclass(obj):
        return False

    return inspect.isclass(obj)
                                        

def is_dataclass_instance(obj: Any) -> TypeGuard[Dataclass]:
    return is_dataclass_type(type(obj))


def is_mongoclass(obj: Any) -> TypeGuard[Union[Mongoclass, Type[Mongoclass]]]:
    if not is_dataclass(obj):
        return False

    if "collection" not in obj.__dataclass_fields__:
        return False

    if obj.__dataclass_fields__["collection"]._field_type is not _FIELD_CLASSVAR:
        return False

    if "_id" in obj.__dataclass_fields__:
        return True

    for field in fields(obj):
        field_name = get_field_name(field)
        if field_name == "_id":
            return True

    return False


def is_mongoclass_type(obj: Any) -> TypeGuard[Type[Mongoclass]]:
    if not is_mongoclass(obj):
        return False

    return inspect.isclass(obj)


def is_mongoclass_instance(obj: Any) -> TypeGuard[Mongoclass]:
    return is_mongoclass_type(type(obj))

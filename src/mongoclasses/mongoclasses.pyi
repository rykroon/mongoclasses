from abc import ABCMeta
from dataclasses import Field
from typing import Any, Callable, TypeGuard, TYPE_CHECKING

from pymongo.collection import Collection
from pymongo.database import Database
from motor.motor_asyncio import AsyncIOMotorCollection, AsyncIOMotorDatabase

if TYPE_CHECKING:
    from _typeshed import DataclassInstance


class Config(DataclassInstance):
    collection: Collection | AsyncIOMotorCollection
    id_field: Field
    auto_now_fields: list[str]
    auto_now_add_fields: list[str]


class MongoclassInstance(DataclassInstance, metaclass=ABCMeta):
    __mongoclass_config__: Config

def mongoclass(
    db: Database | AsyncIOMotorDatabase, collection_name: str | None, **kwargs: Any
) -> Callable[[type], MongoclassInstance]:
    pass

def is_mongoclass(
    obj: Any, /
) -> TypeGuard[MongoclassInstance | type[MongoclassInstance]]:
    pass

def _is_mongoclass_instance(obj: Any) -> TypeGuard[MongoclassInstance]:
    pass

def _get_collection(
    obj: MongoclassInstance | type[MongoclassInstance],
) -> Collection | AsyncIOMotorCollection:
    pass

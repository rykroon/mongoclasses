from abc import ABCMeta
from typing import Any, ClassVar, TypeGuard, TYPE_CHECKING

from pymongo.collection import Collection
from motor.motor_asyncio import AsyncIOMotorCollection

if TYPE_CHECKING:
    from _typeshed import DataclassInstance

class MongoclassInstance(DataclassInstance, metaclass=ABCMeta):
    collection: ClassVar[Collection | AsyncIOMotorCollection]
    _id: Any

def is_mongoclass(
    obj: Any, /
) -> TypeGuard[MongoclassInstance | type[MongoclassInstance]]:
    pass

def _is_mongoclass_instance(obj: Any) -> TypeGuard[MongoclassInstance]:
    pass

def _is_mongoclass_type(t: type, /): pass



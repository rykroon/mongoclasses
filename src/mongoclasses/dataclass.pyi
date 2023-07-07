from abc import ABCMeta
from typing import Any, ClassVar, TypeGuard, TYPE_CHECKING

from pymongo.collection import Collection
from motor.motor_asyncio import AsyncIOMotorCollection

if TYPE_CHECKING:
    from _typeshed import DataclassInstance

class MongoclassInstance(DataclassInstance, metaclass=ABCMeta):
    collection: ClassVar[AsyncIOMotorCollection | Collection]
    _id: Any

def fromdict(cls: type[DataclassInstance], /, data: dict[str, Any]) -> DataclassInstance: ...
def is_mongoclass(
    obj: Any, /
) -> TypeGuard[MongoclassInstance | type[MongoclassInstance]]: ...
def _is_mongoclass_type(obj: type, /) -> TypeGuard[type[MongoclassInstance]]: ...
def _is_mongoclass_instance(obj: Any, /) -> TypeGuard[MongoclassInstance]: ...

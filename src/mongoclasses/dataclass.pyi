from typing import Any, Callable, ClassVar, TypeAlias, TypeGuard, TYPE_CHECKING

from pymongo.collection import Collection
from motor.motor_asyncio import AsyncIOMotorCollection

if TYPE_CHECKING:
    from _typeshed import DataclassInstance

class MongoclassInstance(DataclassInstance):
    collection: ClassVar[AsyncIOMotorCollection | Collection]
    _id: Any

Data: TypeAlias = dict[str, Any]

def fromdict(cls: type[DataclassInstance], /, data: Data) -> DataclassInstance: ...
def is_mongoclass(
    obj: Any, /
) -> TypeGuard[MongoclassInstance | type[MongoclassInstance]]: ...
def is_mongoclass_type(obj: Any, /) -> TypeGuard[type[MongoclassInstance]]: ...
def is_mongoclass_instance(obj: Any, /) -> TypeGuard[MongoclassInstance]: ...
def create_include_dict_factory(
    fields: list[str] | None,
) -> Callable[[list[str, Any]], dict[str, Any]]: ...

from typing import Any, Callable, ClassVar, TypeAlias, TypeGuard, TYPE_CHECKING

from motor.motor_asyncio import AsyncIOMotorCursor, AsyncIOMotorCollection
from pymongo.results import DeleteResult, InsertOneResult, UpdateResult

if TYPE_CHECKING:
    from _typeshed import DataclassInstance

class MongoclassInstance(DataclassInstance):
    collection: ClassVar[AsyncIOMotorCollection]
    _id: Any

Data: TypeAlias = dict[str, Any]

DictFactory: TypeAlias = Callable[[list[tuple[str, Any]]], Data]


def fromdict(cls: type[DataclassInstance], /, data: Data) -> DataclassInstance:
    ...


def is_mongoclass(
    obj: Any, /
) -> TypeGuard[MongoclassInstance | type[MongoclassInstance]]:
    ...


def _is_mongoclass_type(obj: Any, /) -> TypeGuard[type[MongoclassInstance]]:
    ...


def _is_mongoclass_instance(obj: Any, /) -> TypeGuard[MongoclassInstance]:
    ...


def omit_null_id(iterable: list[tuple[str, Any]]) -> Data:
    ...


async def insert_one(
    obj: MongoclassInstance, /, dict_factory: DictFactory = omit_null_id
) -> InsertOneResult:
    ...


async def update_one(
    obj: MongoclassInstance, /, dict_factory: DictFactory = dict
) -> UpdateResult:
    ...


async def delete_one(obj: MongoclassInstance, /) -> DeleteResult:
    ...


async def find_one(
    cls: type[MongoclassInstance],
    /,
    query: Data,
    fromdict: Callable[[type[DataclassInstance], Data], DataclassInstance] = fromdict,
) -> MongoclassInstance | None:
    ...


def find(cls: type[MongoclassInstance], /, query: Data) -> AsyncIOMotorCursor:
    ...

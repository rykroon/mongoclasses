from abc import ABCMeta
from typing import Any, ClassVar, Literal, TypeGuard, TYPE_CHECKING

from pymongo.collection import Collection
from pymongo.results import DeleteResult, InsertOneResult, UpdateResult
from motor.motor_asyncio import AsyncIOMotorCollection

from .utils import Cursor, AsyncCursor

if TYPE_CHECKING:
    from _typeshed import DataclassInstance

class MongoclassInstance(DataclassInstance, metaclass=ABCMeta):
    collection: ClassVar[AsyncIOMotorCollection | Collection]
    _id: Any


def asdict(
    obj: Any, include: list[str] | None, exclude: list[str] | None
) -> dict[str, Any]:
    ...


def is_mongoclass(
    obj: Any, /
) -> TypeGuard[MongoclassInstance | type[MongoclassInstance]]: ...


def _is_mongoclass_type(obj: type, /) -> TypeGuard[type[MongoclassInstance]]: ...


def _is_mongoclass_instance(obj: Any, /) -> TypeGuard[MongoclassInstance]: ...


def insert_one(obj: MongoclassInstance, /) -> InsertOneResult: ...


def update_one(
    obj: MongoclassInstance, /, fields: list[str] | None
) -> UpdateResult: ...


def delete_one(obj: MongoclassInstance, /) -> DeleteResult: ...


def find_one(
    cls: type[MongoclassInstance],
    /,
    filter: dict[str, Any] | None,
) -> MongoclassInstance | None: ...


def find(
    cls: type[MongoclassInstance],
    /,
    filter: dict[str, Any] | None,
    skip: int,
    limit: int,
    sort: list[tuple[str, Literal[1, -1]]] | None,
) -> AsyncCursor | Cursor: ...

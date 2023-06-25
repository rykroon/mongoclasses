from typing import Any, Callable, TypeAlias, TYPE_CHECKING

from motor.motor_asyncio import AsyncIOMotorCursor
from pymongo.cursor import Cursor
from pymongo.results import DeleteResult, InsertOneResult, UpdateResult

from . dataclass import MongoclassInstance, Data


if TYPE_CHECKING:
    from _typeshed import DataclassInstance


DictFactory: TypeAlias = Callable[[list[tuple[str, Any]]], Data]


def insert_one(
    obj: MongoclassInstance, /, dict_factory: DictFactory
) -> InsertOneResult:
    ...


def update_one(
    obj: MongoclassInstance, /, dict_factory: DictFactory
) -> UpdateResult:
    ...


def delete_one(obj: MongoclassInstance, /) -> DeleteResult:
    ...


def find_one(
    cls: type[MongoclassInstance],
    /,
    query: Data,
    fromdict: Callable[[type[DataclassInstance], Data], DataclassInstance],
) -> MongoclassInstance | None:
    ...


def find(cls: type[MongoclassInstance], /, query: Data) -> AsyncIOMotorCursor | Cursor:
    ...

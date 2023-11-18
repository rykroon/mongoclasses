from typing import Any, Literal, TypeVar
from typing_extensions import AsyncIterator, Iterator
from pymongo.cursor import Cursor
from pymongo.results import InsertOneResult, UpdateResult, DeleteResult
from motor.motor_asyncio import AsyncIOMotorCursor

from .types import MongoclassInstance


T = TypeVar("T", bound=MongoclassInstance)

def insert_one(obj: MongoclassInstance, /) -> InsertOneResult:
    pass

async def ainsert_one(obj: MongoclassInstance, /) -> InsertOneResult:
    pass

def update_one(obj: MongoclassInstance, update: dict[str, Any], /) -> UpdateResult:
    pass

async def aupdate_one(
    obj: MongoclassInstance, update: dict[str, Any], /
) -> UpdateResult:
    pass

def replace_one(obj: MongoclassInstance, /, upsert: bool = False) -> UpdateResult:
    pass

async def areplace_one(
    obj: MongoclassInstance, /, upsert: bool = False
) -> UpdateResult:
    pass

def delete_one(obj: MongoclassInstance, /) -> DeleteResult:
    pass

async def adelete_one(obj: MongoclassInstance, /) -> DeleteResult:
    pass

def find_one(cls: type[T], /, filter: Any | None = None) -> T | None:
    pass

async def afind_one(
    cls: type[MongoclassInstance], /, filter: dict[str, Any] | None = None
) -> MongoclassInstance | None:
    pass

def find(
    cls: type[MongoclassInstance],
    /,
    filter: dict[str, Any] | None = None,
    skip: int = 0,
    limit: int = 0,
    sort: list[tuple[str, Literal[1, -1]]] | None = None,
) -> Cursor[Any] | AsyncIOMotorCursor:
    pass

def iter_objects(cls: type[T], cursor: Cursor[Any]) -> Iterator[T]:
    pass

async def aiter_objects(cls: type[T], cursor: AsyncIOMotorCursor) -> AsyncIterator[T]:
    pass

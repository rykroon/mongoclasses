from typing import Any
from pymongo.results import DeleteResult, InsertOneResult, UpdateResult
from .mongoclasses import MongoclassInstance


async def insert_one(obj: MongoclassInstance, /) -> InsertOneResult: ...


async def update_one(
    obj: MongoclassInstance, /, fields: list[str] | None
) -> UpdateResult: ...


async def delete_one(obj: MongoclassInstance, /) -> DeleteResult: ...


async def find_one(
    cls: type[MongoclassInstance],
    /,
    filter: dict[str, Any] | None,
) -> MongoclassInstance | None: ...

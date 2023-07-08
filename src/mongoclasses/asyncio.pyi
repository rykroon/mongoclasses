from typing import Any, Callable, TYPE_CHECKING
from pymongo.results import DeleteResult, InsertOneResult, UpdateResult
from .mongoclasses import MongoclassInstance

if TYPE_CHECKING:
    from _typeshed import DataclassInstance

async def insert_one(obj: MongoclassInstance, /) -> InsertOneResult: ...


async def update_one(
    obj: MongoclassInstance, /, fields: list[str] | None
) -> UpdateResult: ...


async def delete_one(obj: MongoclassInstance, /) -> DeleteResult: ...


async def find_one(
    cls: type[MongoclassInstance],
    /,
    filter: dict[str, Any] | None,
    fromdict: Callable[[type[DataclassInstance], dict[str, Any]], DataclassInstance],
) -> MongoclassInstance | None: ...

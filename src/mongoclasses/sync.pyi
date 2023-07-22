from typing import Any, Literal
from pymongo.results import DeleteResult, InsertOneResult, UpdateResult
from .cursors import Cursor, AsyncCursor
from .mongoclasses import MongoclassInstance

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

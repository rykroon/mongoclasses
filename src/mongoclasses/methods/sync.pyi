from typing import Any
from pymongo.results import DeleteResult, InsertOneResult, UpdateResult
from ..cursors import Cursor, AsyncCursor
from ..mongoclasses import MongoclassInstance

def insert_one(obj: MongoclassInstance, /) -> InsertOneResult: ...
def update_one(
    obj: MongoclassInstance, /, fields: list[str] | None
) -> UpdateResult: pass
def replace_one(obj: MongoclassInstance, /, upsert: bool=False) -> UpdateResult: pass
def delete_one(obj: MongoclassInstance, /) -> DeleteResult: pass
def find_one(
    cls: type[MongoclassInstance],
    /,
    filter: dict[str, Any] | None,
) -> MongoclassInstance | None: pass
def find(
    cls: type[MongoclassInstance],
    /,
    filter: dict[str, Any] | None,
    skip: int,
    limit: int,
    sort: list[str] | None,
) -> AsyncCursor | Cursor: pass

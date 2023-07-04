from typing import Any, Callable, TYPE_CHECKING

from motor.motor_asyncio import AsyncIOMotorCursor
from pymongo.cursor import Cursor
from pymongo.results import DeleteResult, InsertOneResult, UpdateResult

from .dataclass import MongoclassInstance

if TYPE_CHECKING:
    from _typeshed import DataclassInstance

def insert_one(obj: MongoclassInstance, /) -> InsertOneResult: ...
def update_one(obj: MongoclassInstance, /, fields: list[str] | None) -> UpdateResult: ...
def delete_one(obj: MongoclassInstance, /) -> DeleteResult: ...
def find_one(
    cls: type[MongoclassInstance],
    /,
    query: dict[str, Any],
    fromdict: Callable[[type[DataclassInstance], Any], DataclassInstance],
) -> MongoclassInstance | None: ...
def find(
    cls: type[MongoclassInstance], /, query: Any
) -> AsyncIOMotorCursor | Cursor: ...

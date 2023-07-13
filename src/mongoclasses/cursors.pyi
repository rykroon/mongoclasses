from dataclasses import dataclass
from typing import Self, TYPE_CHECKING

from pymongo.cursor import Cursor as PymongoCursor
from motor.motor_asyncio import AsyncIOMotorCursor

if TYPE_CHECKING:
    from _typeshed import DataclassInstance

@dataclass(frozen=True)
class Cursor:
    cursor: PymongoCursor
    dataclass: type[DataclassInstance]

    def __iter__(self) -> Self: ...
    def __next__(self) -> DataclassInstance: ...

@dataclass(frozen=True)
class AsyncCursor:
    cursor: AsyncIOMotorCursor
    dataclass: type[DataclassInstance]

    def __aiter__(self) -> Self: ...
    async def __anext__(self) -> DataclassInstance: ...

from dataclasses import dataclass

from dacite import from_dict, Config
from pymongo.cursor import Cursor as PymongoCursor
from motor.motor_asyncio import AsyncIOMotorCursor


DEFAULT_CONFIG = Config(check_types=False)


@dataclass(frozen=True)
class Cursor:
    cursor: PymongoCursor
    dataclass: type

    def __iter__(self):
        return self

    def __next__(self):
        document = self.cursor.next()
        return from_dict(self.dataclass, document, config=DEFAULT_CONFIG)


@dataclass(frozen=True)
class AsyncCursor:
    cursor: AsyncIOMotorCursor
    dataclass: type

    def __aiter__(self):
        return self

    async def __anext__(self):
        document = await self.cursor.next()
        return from_dict(self.dataclass, document, config=DEFAULT_CONFIG)

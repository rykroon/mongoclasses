from collections.abc import Generator

from pymongo.cursor import Cursor as PymongoCursor
from motor.motor_asyncio import AsyncIOMotorCursor

from .serialization import from_document


def iter_cursor(cls: type, cursor: PymongoCursor) -> Generator:
    for document in cursor:
        yield from_document(cls, document)


async def iter_async_cursor(cls: type, cursor: AsyncIOMotorCursor) -> Generator:
    async for document in cursor:
        yield from_document(cls, document)

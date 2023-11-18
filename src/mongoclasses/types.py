from dataclasses import Field
from typing import Any, ClassVar, Protocol

from pymongo.collection import Collection
from motor.motor_asyncio import AsyncIOMotorCollection


class DataclassInstance(Protocol):
    __dataclass_fields__: ClassVar[dict[str, Field[Any]]]


class MongoclassInstance(DataclassInstance):
    collection: ClassVar[Collection[Any] | AsyncIOMotorCollection]

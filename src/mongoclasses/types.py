from dataclasses import Field
from typing import Any, ClassVar, Dict, Protocol, Union

from pymongo.collection import Collection
from motor.motor_asyncio import AsyncIOMotorCollection


class DataclassInstance(Protocol):
    __dataclass_fields__: ClassVar[Dict[str, Field]]


class MongoclassInstance(DataclassInstance):
    collection: ClassVar[Union[Collection, AsyncIOMotorCollection]]

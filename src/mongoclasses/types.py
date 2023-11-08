from typing import Any, Dict, Protocol, TypeVar, Union
from typing_extensions import TypeGuard

import pydantic
from pymongo.collection import Collection
from motor.motor_asyncio import AsyncIOMotorCollection


def is_pydantic_class_instance(obj: Any) -> bool:
    ...


def is_mongoclass(obj: Any) -> bool:
    ...


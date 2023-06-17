from dataclasses import (
    asdict,
    is_dataclass,
    _FIELD,
    _FIELD_CLASSVAR,
)

import inspect
from typing import Any, Callable, Dict, List, Optional, Type, TypeVar

from motor.motor_asyncio import AsyncIOMotorCursor
from pymongo.results import DeleteResult, InsertOneResult, UpdateResult


__all__ = [
    "fromdict",
    "is_mongoclass",
    "insert_one",
    "update_one",
    "delete_one",
    "find_one",
    "find",
]


T = TypeVar("T")


def fromdict(cls: Type[T], data: Dict[str, Any]) -> T:
    """
    Attempts to create a dataclass instance from a dictionary.
    """
    if not is_dataclass(cls):
        raise TypeError("Object must be a dataclass type.")

    if not inspect.isclass(cls):
        raise TypeError("Object must be a dataclass type.")

    init_values = {}
    non_init_values = []
    for field in cls.__dataclass_fields__.values():
        if field._field_type is _FIELD_CLASSVAR:
            continue

        if field.name not in data:
            continue

        if field.init:
            init_values[field.name] = data[field.name]
        else:
            non_init_values.append(((field.name, data[field.name])))

    obj = cls(**init_values)
    for field, value in non_init_values:
        setattr(obj, field, value)

    return obj


def is_mongoclass(obj) -> bool:
    """
    Returns True if the obj is a a mongoclass or an instance of
    a mongoclass.
    """
    if not is_dataclass(obj):
        return False

    dataclass_fields = getattr(obj, "__dataclass_fields__")
    if "_id" not in dataclass_fields:
        return False

    if dataclass_fields["_id"]._field_type is not _FIELD:
        return False

    if "collection" not in dataclass_fields:
        return False

    if dataclass_fields["collection"]._field_type is not _FIELD_CLASSVAR:
        return False

    return True


def _is_mongoclass_type(obj: Type) -> bool:
    if not inspect.isclass(obj):
        return False
    return is_mongoclass(obj)


def _is_mongoclass_instance(obj) -> bool:
    """
    Returns True if the obj is an instance of a mongoclass.
    """
    return is_mongoclass(type(obj))


async def insert_one(obj, asdict=asdict) -> InsertOneResult:
    if not _is_mongoclass_instance(obj):
        raise TypeError("Object must be a mongoclass instance.")

    document = asdict(obj)
    if document["_id"] is None:
        del document["_id"]

    result: InsertOneResult = await type(obj).collection.insert_one(document)
    obj._id = result.inserted_id
    return result


async def update_one(obj, asdict=asdict) -> UpdateResult:
    if not _is_mongoclass_instance(obj):
        raise TypeError("Object must be a mongoclass instance.")

    document = asdict(obj)
    return await type(obj).collection.update_one(
        filter={"_id": obj._id}, update={"$set": document}
    )


async def delete_one(obj) -> DeleteResult:
    if not _is_mongoclass_instance(obj):
        raise TypeError("Object must be a mongoclass instance.")

    return await type(obj).collection.delete_one({"_id": obj._id})


async def find_one(
    cls: Type[T],
    query: Dict[str, Any],
    fromdict: Callable[[Type[T], Dict[str, Any]], T] = fromdict,
) -> Optional[T]:
    """
    Return a single instance that matches the query on the mongoclass or None.
    """
    if not _is_mongoclass_type(cls):
        raise TypeError("Must be called with a mongoclass type.")

    document = await cls.collection.find_one(query)
    if document is None:
        return None
    return fromdict(cls, document)


def find(cls: Type[T], query: Dict[str, Any]) -> AsyncIOMotorCursor:
    """
    Performs a query on the mongoclass.
    Returns a DocumentCursor.
    """
    if not _is_mongoclass_type(cls):
        raise TypeError("Must be called with a mongoclass type.")

    return cls.collection.find(filter=query)

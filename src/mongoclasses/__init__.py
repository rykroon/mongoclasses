from collections.abc import Callable, Container, Iterable
from dataclasses import asdict, dataclass, fields, is_dataclass
import inspect
from typing import Any

from motor.motor_asyncio import AsyncIOMotorCursor, AsyncIOMotorDatabase
from pymongo.results import DeleteResult, InsertOneResult, UpdateResult


__all__ = [
    "fromdict",
    "include",
    "mongoclass",
    "is_mongoclass",
    "insert_one",
    "update_one",
    "delete_one",
    "find_one",
    "find",
]

_COLLECTION = "__mongoclasses_collection__"


def fromdict(cls, data: dict[str, Any]):
    """
    Attempts to create a dataclass instance from a dictionary.
    """
    if not is_dataclass(cls):
        raise TypeError("Object must be a dataclass type.")

    if not inspect.isclass(cls):
        raise TypeError("Object must be a dataclass type.")

    field_names = set(f.name for f in fields(cls))
    signature = inspect.signature(cls)
    init_param_names = set(signature.parameters)
    non_init_field_names = field_names.difference(init_param_names)

    # initialize object.
    init_data = {p: data[p] for p in init_param_names if p in data}
    ba = signature.bind(**init_data)
    obj = cls(*ba.args, **ba.kwargs)

    # Add remaining fields (if any) using setattr.
    non_init_data = {f: data[f] for f in non_init_field_names if f in data}
    for field, value in non_init_data.items():
        setattr(obj, field, value)

    return obj


def include(
    fields: Container[str],
) -> Callable[[Iterable[tuple[str, Any]]], dict[str, Any]]:
    """
    Returns a dict_factory that will include the fields.
    """

    def include_dict_factory(iterable: Iterable[tuple[str, Any]]) -> dict[str, Any]:
        return {k: v for k, v in iterable if k in fields}

    return include_dict_factory


def mongoclass(
    cls=None,
    /,
    *,
    db: AsyncIOMotorDatabase | None = None,
    collection_name: str = "",
    **kwargs,
):
    def wrap(cls):
        return _process_class(cls, db, collection_name, kwargs)

    # See if we're being called as @dataclass or @dataclass().
    if cls is None:
        # We're called with parens.
        return wrap

    # We're called as @dataclass without parens.
    return wrap(cls)


def _process_class(
    cls,
    db: AsyncIOMotorDatabase,
    collection_name: str,
    dataclass_kwargs: dict[str, Any],
):
    # If the class is not a dataclass, make it a dataclass.
    if not is_dataclass(cls):
        cls = dataclass(**dataclass_kwargs)(cls)

    if not any(f.name == "_id" for f in fields(cls)):
        raise AttributeError("Missing '_id' field.")

    # get parent db if db is None.
    if db is None:
        for base in reversed(cls.mro()):
            if not _is_mongoclass_type(base):
                continue
            db = getattr(base, _COLLECTION).database

    if db is None:
        raise RuntimeError("A database is required.")

    collection_name = collection_name or cls.__name__.lower()
    collection = db[collection_name]
    setattr(cls, _COLLECTION, collection)
    return cls


def is_mongoclass(obj):
    """
    Returns True if the obj is a a mongoclass or an instance of
    a mongoclass.
    """
    cls = obj if inspect.isclass(obj) else type(obj)
    return hasattr(cls, _COLLECTION)


def _is_mongoclass_type(obj):
    return hasattr(obj, _COLLECTION) and inspect.isclass(obj)


def _is_mongoclass_instance(obj):
    """
    Returns True if the obj is an instance of a mongoclass.
    """
    return hasattr(type(obj), _COLLECTION)


async def insert_one(obj, /) -> InsertOneResult:
    if not _is_mongoclass_instance(obj):
        raise TypeError("Object must be a mongoclass instance.")

    document = asdict(obj)
    if document["_id"] is None:
        del document["_id"]

    collection = getattr(obj, _COLLECTION)
    result = await collection.insert_one(document)
    obj._id = result.inserted_id
    return result


async def update_one(obj, /, fields: Iterable[str] | None = None) -> UpdateResult:
    if not _is_mongoclass_instance(obj):
        raise TypeError("Object must be a mongoclass instance.")

    dict_factory = include(fields) if fields is not None else dict
    document = asdict(obj, dict_factory=dict_factory)
    collection = getattr(obj, _COLLECTION)
    return await collection.update_one(
        filter={"_id": obj._id}, update={"$set": document}
    )


async def delete_one(obj, /) -> DeleteResult:
    if not _is_mongoclass_instance(obj):
        raise TypeError("Object must be a mongoclass instance.")

    collection = getattr(obj, _COLLECTION)
    return await collection.delete_one({"_id": obj._id})


async def find_one(cls, query: dict[str, Any]):
    """
    Return a single instance that matches the query on the mongoclass or None.
    """
    if not _is_mongoclass_type(cls):
        raise TypeError("Must be called with a mongoclass type.")

    collection = getattr(cls, _COLLECTION)
    document = await collection.find_one(query)
    if document is None:
        return None
    return fromdict(cls, document)


def find(cls, query: dict[str, Any]) -> AsyncIOMotorCursor:
    """
    Performs a query on the mongoclass.
    Returns a DocumentCursor.
    """
    if not _is_mongoclass_type(cls):
        raise TypeError("Must be called with a mongoclass type.")

    collection = getattr(cls, _COLLECTION)
    return collection.find(filter=query)

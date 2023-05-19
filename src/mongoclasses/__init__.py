from collections.abc import Callable, Iterable
from dataclasses import asdict, dataclass, fields, is_dataclass
import inspect

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
    "find"
]

_COLLECTION = "__mongoclasses_collection__"


def fromdict(cls, data: dict):
    """
    Attempts to create a dataclass instance from a dictionary.
    """
    if not is_dataclass(cls):
        raise TypeError("Object must be a dataclass type.")

    if not inspect.isclass(cls):
        raise TypeError("Object must be a dataclass type.")

    sig = inspect.signature(cls)
    param_names = (param for param in sig.parameters)
    init_kwargs = {param: data[param] for param in param_names if param in data}
    obj = cls(**init_kwargs)

    field_names = set(f.name for f in fields(cls))
    non_init_fields = field_names.difference(param_names)

    for field in non_init_fields:
        if field not in data:
            continue
        setattr(obj, field, data[field])

    return obj


def include(fields: Iterable[str]) -> Callable[[Iterable], dict]:
    """
    Returns a dict_factory that will include the fields.
    """

    def include_dict_factory(iterable: Iterable) -> dict:
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


def _process_class(cls, db, collection_name, dataclass_kwargs):
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

    dict_factory = include(fields) if fields else dict
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


async def find_one(cls, query):
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


def find(cls, query) -> AsyncIOMotorCursor:
    """
    Performs a query on the mongoclass.
    Returns a DocumentCursor.
    """
    if not _is_mongoclass_type(cls):
        raise TypeError("Must be called with a mongoclass type.")

    collection = getattr(cls, _COLLECTION)
    return collection.find(filter=query)

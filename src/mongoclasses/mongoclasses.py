from dataclasses import (
    fields,
    is_dataclass,
    _FIELD,
    _FIELD_CLASSVAR,
    _is_dataclass_instance,
)
from functools import lru_cache
import inspect

from dacite import from_dict, Config
from motor.motor_asyncio import AsyncIOMotorCursor

from .utils import Cursor, AsyncCursor


DEFAULT_CONFIG = Config(check_types=False)


def asdict(obj, include=None, exclude=None):
    """
    Converts a dataclass instance into a dictionary.

    Parameters:
        obj: A dataclass instance.
        include: A list of fields to include in the dictionary.
        exclude: A list of fields to exclude from the dictionary.

    Returns:
        A dictionary.
    """
    if not _is_dataclass_instance(obj):
        raise TypeError("asdict() should be called on dataclass instances")

    if include is not None and exclude is not None:
        raise ValueError("include and exclude cannot be used together.")

    result = ((f.name, _asdict(getattr(obj, f.name))) for f in fields(obj))

    if include is not None:
        result = filter(lambda x: x[0] in include, result)

    elif exclude is not None:
        result = filter(lambda x: x[0] not in exclude, result)

    return dict(result)


def _asdict(value):
    """
    This asdict() function makes a few assumptions since it is being used within the
    context of MongoDB.
    1) dictionary keys are assumed to be strings.
    2) tuples, sets, and frozensets are converted into a list (array). since those types
        do not exist in mongoDB.
    """
    if _is_dataclass_instance(value):
        return {f.name: _asdict(getattr(value, f.name)) for f in fields(value)}

    elif isinstance(value, (list, tuple, set, frozenset)):
        return [_asdict(i) for i in value]

    elif isinstance(value, dict):
        return {k: _asdict(v) for k, v in value.items()}

    else:
        return value


def is_mongoclass(obj, /):
    """
    Returns True if the object is a mongoclass type or instance else False.

    Parameters:
        obj: Any object.

    Returns:
        True if the object is a mongoclass type or instance.
    """
    if not inspect.isclass(obj):
        obj = type(obj)
    return _is_mongoclass_type(obj)


def _is_mongoclass_instance(obj, /):
    return _is_mongoclass_type(type(obj))


@lru_cache
def _is_mongoclass_type(obj, /):
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


def insert_one(obj, /):
    """
    Inserts the object into the database.
    If `_id is None` it will be removed from the document before insertion and the
    new inserted id will be added to the object.

    Parameters:
        obj: A mongoclass instance.

    Raises:
        TypeError: If the object is not a mongoclass instance.

    Returns:
        A pymongo `InsertOneResult` object.
    """
    if not _is_mongoclass_instance(obj):
        raise TypeError("Not a mongoclass instance.")

    document = asdict(obj)
    if document["_id"] is None:
        del document["_id"]

    result = type(obj).collection.insert_one(document)
    obj._id = result.inserted_id
    return result


def update_one(obj, /, fields=None):
    """
    Updates the object in the database.

    Parameters:
        obj: A mongoclass instance.
        fields: A list of field names. If provided, only the fields listed will be \
            updated in the database.

    Raises:
        TypeError: If the object is not a mongoclass instance.

    Returns:
        A pymongo `UpdateResult` object.
    """
    if not _is_mongoclass_instance(obj):
        raise TypeError("Not a mongoclass instance.")

    document = asdict(obj, include=fields)
    return type(obj).collection.update_one(
        filter={"_id": obj._id}, update={"$set": document}
    )


def delete_one(obj, /):
    """
    Deletes the object from the database.

    Parameters:
        obj: A mongoclass instance.

    Raises:
        TypeError: If the object is not a mongoclass instance.

    Returns:
        A pymongo `DeleteResult` object.
    """
    if not _is_mongoclass_instance(obj):
        raise TypeError("Not a mongoclass instance.")

    return type(obj).collection.delete_one({"_id": obj._id})


def find_one(cls, /, filter=None):
    """
    Return a single instance that matches the query or None.

    Parameters:
        cls: A mongoclass type.
        filter: A dictionary specifying the query to be performed.

    Raises:
        TypeError: If the class is not a Mongoclass type.

    Returns:
        A mongoclass instance or None.
    """
    if not _is_mongoclass_type(cls):
        raise TypeError("Not a mongoclass type.")

    document = cls.collection.find_one(filter=filter)
    if document is None:
        return None
    return from_dict(cls, document, DEFAULT_CONFIG)


def find(cls, /, filter=None, skip=0, limit=0, sort=None):
    """
    Performs a query on the mongoclass.

    Parameters:
        cls: A mongoclass type.
        filter: A dictionary specifying the query to be performed.
        skip: The number of documents to omit from the start of the result set.
        limit: The maximum number of results to return.
        sort: A list of (key, direction) pairs specifying the sort order for this query.

    Raises:
        TypeError: If the class is not a Mongoclass type.

    Returns:
        A `Cursor` object if the mongoclass's collection is synchronous or an \
            `AsyncCursor` object if the collection is asynchronous.
    """
    if not _is_mongoclass_type(cls):
        raise TypeError("Not a mongoclass type.")

    cursor = cls.collection.find(filter=filter, skip=skip, limit=limit, sort=sort)
    if isinstance(cursor, AsyncIOMotorCursor):
        return AsyncCursor(cursor=cursor, dataclass=cls)
    return Cursor(cursor=cursor, dataclass=cls)

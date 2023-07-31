from dataclasses import asdict
from motor.motor_asyncio import AsyncIOMotorCursor

from .cursors import AsyncCursor, Cursor
from .mongoclasses import (
    is_mongoclass,
    _is_mongoclass_instance,
    _get_id_field,
    _get_collection,
)


def insert_one(obj, /):
    """
    Inserts the object into the database.

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
    collection = _get_collection(obj)
    result = collection.insert_one(document)
    id_field = _get_id_field(obj)
    setattr(obj, id_field.name, result.inserted_id)
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

    document = asdict(obj)
    if fields is not None:
        document = {k: v for k, v in document.items() if k in fields}

    id_field = _get_id_field(obj)
    id_value = getattr(obj, id_field.name)
    collection = _get_collection(obj)
    return collection.update_one(filter={"_id": id_value}, update={"$set": document})


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

    id_field = _get_id_field(obj)
    id_value = getattr(obj, id_field.name)
    collection = _get_collection(obj)
    return collection.delete_one({"_id": id_value})


def find_one(cls, /, filter=None):
    """
    Return a single instance that matches the query or None.

    Parameters:
        cls: A mongoclass type.
        filter: A dictionary specifying the query to be performed.

    Raises:
        TypeError: If the class is not a mongoclass.

    Returns:
        A mongoclass instance or None.
    """
    if not is_mongoclass(cls):
        raise TypeError("Not a mongoclass.")

    collection = _get_collection(cls)
    document = collection.find_one(filter=filter)
    if document is None:
        return None
    return converter.structure(document, cls)


def find(cls, /, filter=None, skip=0, limit=0, sort=None):
    """
    Performs a query on the mongoclass.

    Parameters:
        cls: A mongoclass.
        filter: A dictionary specifying the query to be performed.
        skip: The number of documents to omit from the start of the result set.
        limit: The maximum number of results to return.
        sort: A list of fields to sort by. If a field is prepended with a negative \
            sign it will be sorted in descending order. Otherwise ascending.

    Raises:
        TypeError: If the class is not a Mongoclass type.

    Returns:
        A `Cursor` object if the mongoclass's collection is synchronous or an \
            `AsyncCursor` object if the collection is asynchronous.
    """
    if not is_mongoclass(cls):
        raise TypeError("Not a mongoclass.")

    if sort is not None:
        sort = [(f[1:], -1) if f.startswith("-") else (f, 1) for f in sort]

    collection = _get_collection(cls)
    cursor = collection.find(filter=filter, skip=skip, limit=limit, sort=sort)
    if isinstance(cursor, AsyncIOMotorCursor):
        return AsyncCursor(cursor=cursor, dataclass=cls)
    return Cursor(cursor=cursor, dataclass=cls)

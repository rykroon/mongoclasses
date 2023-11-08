from motor.motor_asyncio import AsyncIOMotorCursor

from .cursors import AsyncCursor, Cursor
from .mongoclasses import is_mongoclass, _is_mongoclass_instance
from .serialization import to_document, from_document


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

    document = to_document(obj)
    result = type(obj).collection.insert_one(document)
    obj._id = result.inserted_id
    return result


async def ainsert_one(obj, /):
    if not _is_mongoclass_instance(obj):
        raise TypeError("Not a mongoclass instance.")

    document = to_document(obj)
    result = await type(obj).collection.insert_one(document)
    obj._id = result.inserted_id
    return result


def update_one(obj, update, /):
    """
    Updates the object in the database.

    Parameters:
        obj: A mongoclass instance.
        update: An update document.

    Raises:
        TypeError: If the object is not a mongoclass instance.

    Returns:
        A pymongo `UpdateResult` object.
    """
    if not _is_mongoclass_instance(obj):
        raise TypeError("Not a mongoclass instance.")

    return type(obj).collection.update_one(filter={"_id": obj._id}, update=update)


async def aupdate_one(obj, update, /):
    if not _is_mongoclass_instance(obj):
        raise TypeError("Not a mongoclass instance.")

    return await type(obj).collection.update_one(filter={"_id": obj._id}, update=update)


def replace_one(obj, /, upsert=False):
    """
    Replaces the object in the database.

    Parameters:
        obj: A mongoclass instance.
        upsert: If True, will insert the document if it does not already exist.

    Raises:
        TypeError: If the object is not a mongoclass instance.

    Returns:
        A pymongo `UpdateResult` object.
    """
    if not _is_mongoclass_instance(obj):
        raise TypeError("Not a mongoclass instance.")

    document = to_document(obj)
    return type(obj).collection.replace_one(
        filter={"_id": obj._id}, replacement=document, upsert=upsert
    )


async def areplace_one(obj, /, upsert=False):
    if not _is_mongoclass_instance(obj):
        raise TypeError("Not a mongoclass instance.")

    document = to_document(obj)
    return await type(obj).collection.replace_one(
        filter={"_id": obj._id}, replacement=document, upsert=upsert
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


async def adelete_one(obj, /):
    if not _is_mongoclass_instance(obj):
        raise TypeError("Not a mongoclass instance.")

    return await type(obj).collection.delete_one({"_id": obj._id})


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

    document = cls.collection.find_one(filter=filter)
    if document is None:
        return None
    return from_document(cls, document)


async def afind_one(cls, /, filter=None):
    if not is_mongoclass(cls):
        raise TypeError("Not a mongoclass.")

    document = await cls.collection.find_one(filter=filter)
    if document is None:
        return None
    return from_document(cls, document)


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

    cursor = cls.collection.find(filter=filter, skip=skip, limit=limit, sort=sort)
    if isinstance(cursor, AsyncIOMotorCursor):
        return AsyncCursor(cursor=cursor, dataclass=cls)
    return Cursor(cursor=cursor, dataclass=cls)

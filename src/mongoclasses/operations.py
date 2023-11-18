from pymongo.results import InsertOneResult, UpdateResult, DeleteResult

from .serialization import to_document, from_document
from .utils import get_id, set_id, is_mongoclass, is_mongoclass_instance


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
    if not is_mongoclass_instance(obj):
        raise TypeError("Not a mongoclass instance.")

    document = to_document(obj)
    result = type(obj).collection.insert_one(document)
    set_id(obj, result.inserted_id)
    return result


async def ainsert_one(obj, /):
    if not is_mongoclass_instance(obj):
        raise TypeError("Not a mongoclass instance.")

    document = to_document(obj)
    result = await type(obj).collection.insert_one(document)
    assert isinstance(result, InsertOneResult)
    set_id(obj, result.inserted_id)
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
    if not is_mongoclass_instance(obj):
        raise TypeError("Not a mongoclass instance.")

    return type(obj).collection.update_one(filter={"_id": get_id(obj)}, update=update)


async def aupdate_one(obj, update, /):
    if not is_mongoclass_instance(obj):
        raise TypeError("Not a mongoclass instance.")

    result = await type(obj).collection.update_one(
        filter={"_id": get_id(obj)}, update=update
    )
    assert isinstance(result, UpdateResult)
    return result


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
    if not is_mongoclass_instance(obj):
        raise TypeError("Not a mongoclass instance.")

    document = to_document(obj)
    return type(obj).collection.replace_one(
        filter={"_id": get_id(obj)}, replacement=document, upsert=upsert
    )


async def areplace_one(obj, /, upsert=False):
    if not is_mongoclass_instance(obj):
        raise TypeError("Not a mongoclass instance.")

    document = to_document(obj)
    result = await type(obj).collection.replace_one(
        filter={"_id": get_id(obj)}, replacement=document, upsert=upsert
    )
    assert isinstance(result, UpdateResult)
    return result


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
    if not is_mongoclass_instance(obj):
        raise TypeError("Not a mongoclass instance.")

    return type(obj).collection.delete_one({"_id": get_id(obj)})


async def adelete_one(obj, /):
    if not is_mongoclass_instance(obj):
        raise TypeError("Not a mongoclass instance.")

    result = await type(obj).collection.delete_one({"_id": get_id(obj)})
    assert isinstance(result, DeleteResult)
    return result


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

    return cls.collection.find(filter=filter, skip=skip, limit=limit, sort=sort)


def iter_objects(cls, cursor):
    for document in cursor:
        yield from_document(cls, document)


async def aiter_objects(cls, cursor):
    async for document in cursor:
        yield from_document(cls, document)

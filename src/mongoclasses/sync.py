from motor.motor_asyncio import AsyncIOMotorCursor

from .converters import converter
from .cursors import AsyncCursor, Cursor
from .mongoclasses import _is_mongoclass_instance, _is_mongoclass_type


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

    document = converter.unstructure(obj)
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

    document = converter.unstructure(obj)
    if fields is not None:
        document = {k: v for k, v in document.items() if k in fields}
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
    return converter.structure(document, cls)


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
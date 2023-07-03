from dataclasses import asdict
from .dataclass import (
    fromdict, create_include_dict_factory, _is_mongoclass_instance, _is_mongoclass_type
)


def insert_one(obj, /):
    """
    Inserts the object into the database.
    If `_id is None` it will be removed from the document before insertion and the
    new inserted id will be added to the object.

    **Parameters:**

    * **obj** - A mongoclass instance.

    **Returns:** `InsertOneResult`
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

    **Parameters:**

    * **obj** - A mongoclass instance.
    * **fields** - A list of field names. If provided, only the fields listed will be
    updated in the database.

    **Returns:** `UpdateResult`
    """
    if not _is_mongoclass_instance(obj):
        raise TypeError("Not a mongoclass instance.")

    dict_factory = dict if fields is None else create_include_dict_factory(fields)
    document = asdict(obj, dict_factory=dict_factory)
    return type(obj).collection.update_one(
        filter={"_id": obj._id}, update={"$set": document}
    )


def delete_one(obj, /):
    """
    Deletes the object from the database.

    **Parameters:**

    * **obj** - A mongoclass instance.

    **Returns:** `DeleteResult`
    """
    if not _is_mongoclass_instance(obj):
        raise TypeError("Not a mongoclass instance.")

    return type(obj).collection.delete_one({"_id": obj._id})


def find_one(cls, /, query, fromdict=fromdict):
    """
    Return a single instance that matches the query.

    **Parameters:**

    * **cls** - A mongoclass type.
    * **query** - A dictionary representing a MongoDB query.
    * **fromdict** - The fromdict function to be used.

    **Returns:** - `DataclassInstance | None`
    """
    if not _is_mongoclass_type(cls):
        raise TypeError("Not a mongoclass type.")

    document = cls.collection.find_one(query)
    if document is None:
        return None
    return fromdict(cls, document)


def find(cls, /, query):
    """
    Performs a query on the mongoclass.

    **Parameters:**

    * **cls** - A mongoclass type.
    * **query** - A dictionary representing a MongoDB query.

    **Returns:** `Cursor | AsyncIOMotorCursor`

    """
    if not _is_mongoclass_type(cls):
        raise TypeError("Not a mongoclass type.")

    return cls.collection.find(filter=query)

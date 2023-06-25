from dataclasses import asdict
from .dataclass import (
    fromdict, is_mongoclass_instance, is_mongoclass_type, omit_null_id
)



def insert_one(obj, /, dict_factory=omit_null_id):
    if not is_mongoclass_instance(obj):
        raise TypeError("Object must be a mongoclass instance.")

    document = asdict(obj, dict_factory=dict_factory)
    result = type(obj).collection.insert_one(document)
    obj._id = result.inserted_id
    return result


def update_one(obj, /, dict_factory=dict):
    if not is_mongoclass_instance(obj):
        raise TypeError("Object must be a mongoclass instance.")

    document = asdict(obj, dict_factory=dict_factory)
    return type(obj).collection.update_one(
        filter={"_id": obj._id}, update={"$set": document}
    )


def delete_one(obj, /):
    if not is_mongoclass_instance(obj):
        raise TypeError("Object must be a mongoclass instance.")

    return type(obj).collection.delete_one({"_id": obj._id})


def find_one(cls, /, query, fromdict=fromdict):
    """
    Return a single instance that matches the query on the mongoclass or None.
    """
    if not is_mongoclass_type(cls):
        raise TypeError("Must be called with a mongoclass type.")

    document = cls.collection.find_one(query)
    if document is None:
        return None
    return fromdict(cls, document)


def find(cls, /, query):
    """
    Performs a query on the mongoclass.
    Returns a DocumentCursor.
    """
    if not is_mongoclass_type(cls):
        raise TypeError("Must be called with a mongoclass type.")

    return cls.collection.find(filter=query)

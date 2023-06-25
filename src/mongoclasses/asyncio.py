from dataclasses import asdict
from .dataclass import (
    fromdict, is_mongoclass_instance, is_mongoclass_type, omit_null_id
)


async def insert_one(obj, /, dict_factory=omit_null_id):
    if not is_mongoclass_instance(obj):
        raise TypeError("Object must be a mongoclass instance.")

    document = asdict(obj, dict_factory=dict_factory)
    result = await type(obj).collection.insert_one(document)
    obj._id = result.inserted_id
    return result


async def update_one(obj, /, dict_factory=dict):
    if not is_mongoclass_instance(obj):
        raise TypeError("Object must be a mongoclass instance.")

    document = asdict(obj, dict_factory=dict_factory)
    return await type(obj).collection.update_one(
        filter={"_id": obj._id}, update={"$set": document}
    )


async def delete_one(obj, /):
    if not is_mongoclass_instance(obj):
        raise TypeError("Object must be a mongoclass instance.")

    return await type(obj).collection.delete_one({"_id": obj._id})


async def find_one(cls, /, query, fromdict=fromdict):
    """
    Return a single instance that matches the query on the mongoclass or None.
    """
    if not is_mongoclass_type(cls):
        raise TypeError("Must be called with a mongoclass type.")

    document = await cls.collection.find_one(query)
    if document is None:
        return None
    return fromdict(cls, document)
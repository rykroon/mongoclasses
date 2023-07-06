from dataclasses import asdict
from .dataclass import (
    fromdict, _is_mongoclass_instance, _is_mongoclass_type
)


async def insert_one(obj, /):
    if not _is_mongoclass_instance(obj):
        raise TypeError("Not a mongoclass instance.")

    document = asdict(obj)
    if document["_id"] is None:
        del document["_id"]

    result = await type(obj).collection.insert_one(document)
    obj._id = result.inserted_id
    return result


async def update_one(obj, /, fields=None):
    if not _is_mongoclass_instance(obj):
        raise TypeError("Not a mongoclass instance.")

    document = asdict(obj)
    if fields is not None:
        document = {k: v for k, v in document.items() if k in fields}

    return await type(obj).collection.update_one(
        filter={"_id": obj._id}, update={"$set": document}
    )


async def delete_one(obj, /):
    if not _is_mongoclass_instance(obj):
        raise TypeError("Not a mongoclass instance.")

    return await type(obj).collection.delete_one({"_id": obj._id})


async def find_one(cls, /, query, fromdict=fromdict):
    """
    Return a single instance that matches the query on the mongoclass or None.
    """
    if not _is_mongoclass_type(cls):
        raise TypeError("Not a mongoclass type.")

    document = await cls.collection.find_one(query)
    if document is None:
        return None
    return fromdict(cls, document)

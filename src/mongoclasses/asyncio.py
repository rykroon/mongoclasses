from dataclasses import asdict

from .mongoclasses import is_mongoclass, _is_mongoclass_instance, fromdict


async def insert_one(obj, /):
    if not _is_mongoclass_instance(obj):
        raise TypeError("Not a mongoclass instance.")

    document = asdict(obj)
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


async def find_one(cls, /, filter=None):
    if not is_mongoclass(cls):
        raise TypeError("Not a mongoclass.")

    document = await cls.collection.find_one(filter=filter)
    if document is None:
        return None
    return fromdict(cls, document)

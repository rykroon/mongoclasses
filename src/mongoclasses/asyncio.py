from .mongoclasses import (
    is_mongoclass, _is_mongoclass_instance
)
from .serialization import to_document, from_document
from .update import to_update_expr


async def insert_one(obj, /):
    if not _is_mongoclass_instance(obj):
        raise TypeError("Not a mongoclass instance.")

    document = to_document(obj)
    result = await type(obj).collection.insert_one(document)
    obj._id = result.inserted_id
    return result


async def update_one(obj, /, fields=None):
    if not _is_mongoclass_instance(obj):
        raise TypeError("Not a mongoclass instance.")

    update_document = to_update_expr(obj, include=fields)
    return await type(obj).collection.update_one(
        filter={"_id": obj._id}, update=update_document
    )


async def replace_one(obj, /):
    if not _is_mongoclass_instance(obj):
        raise TypeError("Not a mongoclass instance.")
    
    document = to_document(obj)
    return await type(obj).collection.replace_one(
        filter={"_id": obj._id}, replacement=document
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
    return from_document(cls, document)

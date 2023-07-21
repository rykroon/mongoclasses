from .converters import converter
from .mongoclasses import (
    is_mongoclass, _is_mongoclass_instance, _get_collection, _get_id_field
)


async def insert_one(obj, /):
    if not _is_mongoclass_instance(obj):
        raise TypeError("Not a mongoclass instance.")

    document = converter.unstructure(obj)
    collection = _get_collection(obj)
    result = await collection.insert_one(document)
    id_field = _get_id_field(obj)
    setattr(obj, id_field.name, result.inserted_id)
    return result


async def update_one(obj, /, fields=None):
    if not _is_mongoclass_instance(obj):
        raise TypeError("Not a mongoclass instance.")

    document = converter.unstructure(obj)
    if fields is not None:
        document = {k: v for k, v in document.items() if k in fields}

    id_field = _get_id_field(obj)
    id_value = getattr(obj, id_field.name)
    collection = _get_collection(obj)
    return await collection.update_one(
        filter={"_id": id_value}, update={"$set": document}
    )


async def delete_one(obj, /):
    if not _is_mongoclass_instance(obj):
        raise TypeError("Not a mongoclass instance.")

    id_field = _get_id_field(obj)
    id_value = getattr(obj, id_field.name)
    collection = _get_collection(obj)
    return await collection.delete_one({"_id": id_value})


async def find_one(cls, /, filter=None):
    if not is_mongoclass(cls):
        raise TypeError("Not a mongoclass.")

    collection = _get_collection(cls)
    document = await collection.find_one(filter=filter)
    if document is None:
        return None
    return converter.structure(document, cls)

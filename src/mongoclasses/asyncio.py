from datetime import datetime

from .converters import converter
from .mongoclasses import is_mongoclass, _is_mongoclass_instance, _get_config


async def insert_one(obj, /):
    if not _is_mongoclass_instance(obj):
        raise TypeError("Not a mongoclass instance.")

    config = _get_config(obj)
    # auto_now_add
    for field in config.auto_now_add_fields:
        setattr(obj, field, datetime.utcnow())

    document = converter.unstructure(obj)
    result = await config.collection.insert_one(document)
    setattr(obj, config.id_field.name, result.inserted_id)
    return result


async def update_one(obj, /, fields=None):
    if not _is_mongoclass_instance(obj):
        raise TypeError("Not a mongoclass instance.")

    config = _get_config(obj)

    # auto now
    for field in config.auto_now_fields:
        setattr(obj, field, datetime.utcnow())

    document = converter.unstructure(obj)
    if fields is not None:
        document = {k: v for k, v in document.items() if k in fields}

    id_value = getattr(obj, config.id_field.name)
    return await config.collection.update_one(
        filter={"_id": id_value}, update={"$set": document}
    )


async def delete_one(obj, /):
    if not _is_mongoclass_instance(obj):
        raise TypeError("Not a mongoclass instance.")

    config = _get_config(obj)
    id_value = getattr(obj, config.id_field.name)
    return await config.collection.delete_one({"_id": id_value})


async def find_one(cls, /, filter=None):
    if not is_mongoclass(cls):
        raise TypeError("Not a mongoclass.")

    config = _get_config(cls)
    document = await config.collection.find_one(filter=filter)
    if document is None:
        return None
    return converter.structure(document, cls)

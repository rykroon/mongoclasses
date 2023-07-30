from dataclasses import dataclass, is_dataclass, fields, Field
from functools import lru_cache
import inspect

from pymongo.collection import Collection
from motor.motor_asyncio import AsyncIOMotorCollection


@dataclass(frozen=True)
class Config:
    """
        mongoclasses config
    """
    collection: Collection | AsyncIOMotorCollection
    id_field: Field
    auto_now_fields: list[str]
    auto_now_add_fields: list[str]


def mongoclass(db, collection_name=None):
    """
    Transforms a class into a Mongoclass. If the class isn't already a dataclass then \
    it will transform the class into a dataclass as well.

    Parameters:
        db: A pymongo Database or motor AsyncioMotorDatabase object.
        collection_name: The name of the collection. Defaults to the class name in all \
        lowercase.

    Raises:
        TypeError if object is not a class, or does not have an _id field.

    Returns:
        A class decorator that transforms the class into a mongoclass.
    """

    def wrapper(cls):
        return _process_class(cls, db, collection_name)

    return wrapper


def _process_class(cls, db, collection_name):
    if not inspect.isclass(cls):
        raise TypeError("object is not a class.")

    if not is_dataclass(cls):
        # if not a dataclass then make it one!
        cls = dataclass(cls)

    if collection_name is None:
        collection_name = cls.__name__.lower()

    setattr(cls, "__mongoclass_collection__", db[collection_name])
    _get_id_field(cls) # will raise a TypeError if _id field is not found.
    return cls


def _get_collection(obj):
    return getattr(obj, "__mongoclass_collection__")


def _get_db_field_name(field):
    return field.metadata.get("mongoclasses", {}).get("db_field", field.name)


@lru_cache
def _get_id_field(obj):
    for field in fields(obj):
        db_field = _get_db_field_name(field)
        if db_field == "_id":
            return field
    raise TypeError("Missing _id field.")


def _is_mongoclass_instance(obj, /):
    return hasattr(type(obj), "__mongoclass_collection__")


def is_mongoclass(obj, /):
    """
    Returns True if the object is a mongoclass type or instance else False.

    Parameters:
        obj: Any object.

    Returns:
        True if the object is a mongoclass type or instance.
    """
    cls = obj if isinstance(obj, type) else type(obj)
    return hasattr(cls, "__mongoclass_collection__")

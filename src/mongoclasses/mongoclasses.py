from dataclasses import dataclass, is_dataclass, fields, Field, MISSING
import inspect

from pymongo.collection import Collection
from motor.motor_asyncio import AsyncIOMotorCollection

from cattrs.gen import override
from .converters import register_db_field_overrides


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

    collection = db[collection_name]
    id_field = None
    db_field_overrides = {}
    auto_now_fields = []
    auto_now_add_fields = []

    for field in fields(cls):
        # check for id field.
        db_field = field.metadata.get("mongoclasses", {}).get("db_field", field.name)
        if db_field == "_id":
            id_field = field

        # add db_field override.
        if db_field != field.name:
            db_field_overrides[field.name] = override(rename=db_field)

        # check for auto now fields.
        auto_now = field.metadata.get("mongoclasses", {}).get("auto_now", False)
        auto_now_add = field.metadata.get("mongoclasses", {}).get("auto_now_add", False)

        if auto_now and auto_now_add:
            raise ValueError("auto_now and auto_now_add are mutually exclusive.")
        
        has_default = field.default is not MISSING or field.default_factory is not MISSING
        if has_default and (auto_now or auto_now_add):
            raise ValueError("Cannot specify a default value with auto_now or auto_now_add.")
        
        if auto_now:
            auto_now_fields.append(field.name)

        if auto_now_add:
            auto_now_add_fields.append(field.name)

    if id_field is None:
        raise TypeError("Must specify an _id field.")

    # register db field overrides.
    register_db_field_overrides(cls, db_field_overrides)

    config = Config(
        collection=collection,
        id_field=id_field,
        auto_now_fields=auto_now_fields,
        auto_now_add_fields=auto_now_add_fields,
    )

    setattr(cls, "__mongoclass_config__", config)
    return cls


def _get_config(obj):
    return getattr(obj, "__mongoclass_config__")

def _get_collection(obj):
    return getattr(obj, "__mongoclass_config__").collection


def _get_id_field(obj):
    return getattr(obj, "__mongoclass_config__").id_field


def _is_mongoclass_instance(obj, /):
    return hasattr(type(obj), "__mongoclass_config__")


def is_mongoclass(obj, /):
    """
    Returns True if the object is a mongoclass type or instance else False.

    Parameters:
        obj: Any object.

    Returns:
        True if the object is a mongoclass type or instance.
    """
    cls = obj if isinstance(obj, type) else type(obj)
    return hasattr(cls, "__mongoclass_config__")
        
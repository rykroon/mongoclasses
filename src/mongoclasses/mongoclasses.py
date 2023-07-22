from dataclasses import dataclass, is_dataclass, fields
import inspect

from .converters import register_db_name_overrides


def mongoclass(db, collection_name=None):
    """
    Parameters:
        db: A pymongo Database or motor AsyncioMotorDatabase object.
        collection_name: Optional collection name. Defaults to the class name is all
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

    # find _id field
    for field in fields(cls):
        field_name = field.metadata.get("mongoclasses", {}).get("db_name", field.name)
        if field_name == "_id":
            setattr(cls, "__mongoclass_id_field__", field)
            break

    else:
        raise TypeError("Must define an '_id' field.")

    register_db_name_overrides(cls)
    return cls


def _get_collection(obj):
    return getattr(obj, "__mongoclass_collection__")


def _get_id_field(obj):
    return getattr(obj, "__mongoclass_id_field__")


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

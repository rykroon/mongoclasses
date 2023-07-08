from dataclasses import (
    fields,
    is_dataclass,
    MISSING,
    _FIELD,
    _FIELD_CLASSVAR,
    _is_dataclass_instance,
)
from functools import lru_cache
import inspect


def asdict(obj, include=None, exclude=None):
    if not _is_dataclass_instance(obj):
        raise TypeError("asdict() should be called on dataclass instances")

    if include is not None and exclude is not None:
        raise ValueError("include and exclude cannot be used together.")

    if include is not None:
        return {
            f.name: _asdict(getattr(obj, f.name))
            for f in fields(obj)
            if f.name in include
        }

    if exclude is not None:
        return {
            f.name: _asdict(getattr(obj, f.name))
            for f in fields(obj)
            if f.name not in exclude
        }

    return {f.name: _asdict(getattr(obj, f.name)) for f in fields(obj)}


def _asdict(value):
    """
    This asdict() function makes a few assumptions since it is being used within the
    context of MongoDB.
    1) dictionary keys are assumed to be strings.
    2) tuples, sets, and frozensets are converted into a list (array). since those types
        do not exist in mongoDB.
    """
    if _is_dataclass_instance(value):
        return {f.name: _asdict(getattr(value, f.name)) for f in fields(value)}

    elif isinstance(value, (list, tuple, set, frozenset)):
        return [_asdict(i) for i in value]

    elif isinstance(value, dict):
        return {k: _asdict(v) for k, v in value.items()}

    else:
        return value


def fromdict(cls, /, data):
    """
    Creates a dataclass instance from a dictionary.

    Parameters:
        data: A dictionary containing the data to create the dataclass.

    Returns:
        A dataclass instance.
    """
    init_values = {}
    non_init_values = {}

    for field in cls.__dataclass_fields__.values():
        if field._field_type is _FIELD_CLASSVAR:
            continue

        if field.name in data:
            value = data[field.name]

        elif field.default is not MISSING:
            value = field.default

        elif field.default_factory is not MISSING:
            value = field.default_factory()

        else:
            continue

        if is_dataclass(field.type):
            value = fromdict(field.type, value)

        if field.init:
            init_values[field.name] = value
        else:
            non_init_values[field.name] = value

    obj = cls(**init_values)
    for field, value in non_init_values.items():
        setattr(obj, field, value)

    return obj


def is_mongoclass(obj, /):
    """
    Returns True if the object is a mongoclass type or instance else False.

    Parameters:
        obj: Any object.

    Returns:
        True if the object is a mongoclass type or instance.
    """
    if not inspect.isclass(obj):
        obj = type(obj)
    return _is_mongoclass_type(obj)


def _is_mongoclass_instance(obj, /):
    return _is_mongoclass_type(type(obj))


@lru_cache
def _is_mongoclass_type(obj, /):
    if not is_dataclass(obj):
        return False

    dataclass_fields = getattr(obj, "__dataclass_fields__")
    if "_id" not in dataclass_fields:
        return False

    if dataclass_fields["_id"]._field_type is not _FIELD:
        return False

    if "collection" not in dataclass_fields:
        return False

    if dataclass_fields["collection"]._field_type is not _FIELD_CLASSVAR:
        return False

    return True


def insert_one(obj, /):
    """
    Inserts the object into the database.
    If `_id is None` it will be removed from the document before insertion and the
    new inserted id will be added to the object.

    Parameters:
        obj: A mongoclass instance.

    Raises:
        TypeError: If the object is not a mongoclass instance.

    Returns:
        A pymongo `InsertOneResult` object.
    """
    if not _is_mongoclass_instance(obj):
        raise TypeError("Not a mongoclass instance.")

    document = asdict(obj)
    if document["_id"] is None:
        del document["_id"]

    result = type(obj).collection.insert_one(document)
    obj._id = result.inserted_id
    return result


def update_one(obj, /, fields=None):
    """
    Updates the object in the database.

    Parameters:
        obj: A mongoclass instance.
        fields: A list of field names. If provided, only the fields listed will be \
            updated in the database.

    Raises:
        TypeError: If the object is not a mongoclass instance.

    Returns:
        A pymongo `UpdateResult` object.
    """
    if not _is_mongoclass_instance(obj):
        raise TypeError("Not a mongoclass instance.")

    document = asdict(obj)
    if fields is not None:
        document = {k: v for k, v in document.items() if k in fields}

    return type(obj).collection.update_one(
        filter={"_id": obj._id}, update={"$set": document}
    )


def delete_one(obj, /):
    """
    Deletes the object from the database.

    Parameters:
        obj: A mongoclass instance.

    Raises:
        TypeError: If the object is not a mongoclass instance.

    Returns:
        A pymongo `DeleteResult` object.
    """
    if not _is_mongoclass_instance(obj):
        raise TypeError("Not a mongoclass instance.")

    return type(obj).collection.delete_one({"_id": obj._id})


def find_one(cls, /, filter=None, fromdict=fromdict):
    """
    Return a single instance that matches the query or None.

    Parameters:
        cls: A mongoclass type.
        filter: A dictionary specifying the query to be performed.
        fromdict: The fromdict function to be used.

    Raises:
        TypeError: If the class is not a Mongoclass type.

    Returns:
        A mongoclass instance or None.
    """
    if not _is_mongoclass_type(cls):
        raise TypeError("Not a mongoclass type.")

    document = cls.collection.find_one(filter=filter)
    if document is None:
        return None
    return fromdict(cls, document)


def find(cls, /, filter=None, skip=0, limit=0, sort=None):
    """
    Performs a query on the mongoclass.

    Parameters:
        cls: A mongoclass type.
        filter: A dictionary specifying the query to be performed.

    Raises:
        TypeError: If the class is not a Mongoclass type.

    Returns:
        A `Cursor` object if the mongoclass's collection is synchronous or an \
            `AsyncIOMotorCursor` object if the collection is asynchronous.
    """
    if not _is_mongoclass_type(cls):
        raise TypeError("Not a mongoclass type.")

    return cls.collection.find(filter=filter, skip=skip, limit=limit, sort=sort)

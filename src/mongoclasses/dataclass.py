from dataclasses import is_dataclass, _FIELD, _FIELD_CLASSVAR
import inspect


def fromdict(cls, /, data):
    """
    Attempts to create a dataclass instance from a dictionary.
    """
    # if not is_dataclass(cls):
    #     raise TypeError("Object must be a dataclass type.")

    # if not inspect.isclass(cls):
    #     raise TypeError("Object must be a dataclass type.")

    init_values = {}
    non_init_values = {}
    is_frozen = cls.__dataclass_params__.frozen

    for field in cls.__dataclass_fields__.values():
        if field._field_type is _FIELD_CLASSVAR:
            continue

        if field.name not in data:
            # should this be strict?
            continue

        value = data[field.name]

        if is_dataclass(field.type):
            # recursive!
            value = fromdict(field.type, value)

        if field.init:
            init_values[field.name] = value
        elif not is_frozen:
            non_init_values[field.name] = value

    obj = cls(**init_values)
    for field, value in non_init_values.items():
        setattr(obj, field, value)

    return obj


def omit_null_id(iterable):
    """
    A dict_factory that omits the _id field if it is None.
    """
    return {k: v for k, v in iterable if k != "_id" or v is not None}


def is_mongoclass(obj, /):
    """
    Returns True if the obj is a mongoclass or an instance of
    a mongoclass.
    """
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


def is_mongoclass_type(obj, /):
    if not inspect.isclass(obj):
        return False
    return is_mongoclass(obj)


def is_mongoclass_instance(obj, /):
    """
    Returns True if the obj is an instance of a mongoclass.
    """
    return is_mongoclass(type(obj))

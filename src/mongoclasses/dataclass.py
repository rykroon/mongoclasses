from dataclasses import is_dataclass, MISSING, _FIELD, _FIELD_CLASSVAR
import inspect


def fromdict(cls, /, data, strict=True):
    """
    Creates a dataclass instance from a dictionary.

    **Parameters:**

    * **data** - A dictionary containing the data with which to be used to create the
    dataclass.
    * **strict** - If True, the default, then all dataclass fields must be present in
    the data dictionary. If False, then the default value of the field will be used. If
    a default value is not present, then a KeyError will be raised.

    **Returns:** `DataclassInstance`
    """
    init_values = {}
    non_init_values = {}

    for field in cls.__dataclass_fields__.values():
        if field._field_type is _FIELD_CLASSVAR:
            continue

        try:
            value = data[field.name]

        except KeyError as e:
            if strict:
                raise e

            if field.default is not MISSING:
                value = field.default
            
            elif field.default_factory is not MISSING:
                value = field.default_factory()

            else:
                raise e

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


def create_include_dict_factory(fields):
    def dict_factory(iterable):
        return {k: v for k, v in iterable if k in fields}

    return dict_factory


def is_mongoclass(obj, /):
    """
    Returns True if the obj is a mongoclass type or instance else False.
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


def _is_mongoclass_type(obj, /):
    if not inspect.isclass(obj):
        return False
    return is_mongoclass(obj)


def _is_mongoclass_instance(obj, /):
    """
    Returns True if the obj is an instance of a mongoclass.
    """
    return is_mongoclass(type(obj))

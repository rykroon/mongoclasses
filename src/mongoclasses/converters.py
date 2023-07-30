from dataclasses import fields, is_dataclass
from datetime import datetime, date
from decimal import Decimal
from re import Pattern
from uuid import UUID

from bson import Binary, DatetimeMS, Decimal128, ObjectId, Regex, SON
import cattrs
from cattrs.gen import make_dict_structure_fn, make_dict_unstructure_fn

from .mongoclasses import is_mongoclass, _get_db_field_name
import logging

converter = cattrs.Converter()


def register_db_field_overrides(cls, mapping):
    """
    Generates the appropriate struct/unstruct functions required to rename the
    dataclass fields.
    """
    unstruct_func = make_dict_unstructure_fn(cls, converter, **mapping)
    struct_func = make_dict_structure_fn(cls, converter, **mapping)
    converter.register_unstructure_hook(cls, unstruct_func)
    converter.register_structure_hook(cls, struct_func)


def register_hook(converter, hook):
    if hasattr(hook, "from_db"):
        converter.register_structure_hook(hook.type_, hook.from_db)

    if hasattr(hook, "to_db"):
        converter.register_unstructure_hook(hook.type_, hook.to_db)


def structure_dataclass(data, dataclass):
    init_fields = {}
    non_init_fields = {}
    for f in fields(dataclass):
        if f.name not in data:
            continue

        value = converter.structure(data[f.name], f.type)
        if f.init:
            init_fields[f.name] = value
        else:
            non_init_fields[f.name] = value

    obj = dataclass(**init_fields)
    for f, v in non_init_fields.items():
        setattr(obj, f, v)
    return obj


def structure_mongoclass(data, mongoclass):
    init_fields = {}
    non_init_fields = {}
    for field in fields(mongoclass):
        db_field = _get_db_field_name(field)
        if db_field not in data:
            continue

        value = converter.structure(data[db_field], field.type)
        if field.init:
            init_fields[field.name] = value
        else:
            non_init_fields[field.name] = value

    obj = mongoclass(**init_fields)
    for f, v in non_init_fields.items():
        setattr(obj, f, v)
    return obj


def unstructure_mongoclass(obj):
    result = {}
    for field in fields(obj):
        value = converter.unstructure(getattr(obj, field.name))
        db_field = _get_db_field_name(field)
        result[db_field] = value
    return result


converter.register_structure_hook_func(
    lambda t: is_dataclass(t) and not is_mongoclass(t), structure_dataclass
)

converter.register_structure_hook_func(lambda t: is_mongoclass(t), structure_mongoclass)

converter.register_unstructure_hook_func(
    lambda t: is_mongoclass(t), unstructure_mongoclass
)


class DateHook:
    type_ = date

    @staticmethod
    def from_db(value, type_):
        return DatetimeHook.from_db(value, type_).date()

    @staticmethod
    def to_db(value):
        # MongoDB does not accept python date objects so it must be converted into a
        # datetime object.
        return datetime(year=value.year, month=value.month, day=value.day)


register_hook(converter, DateHook)


class DatetimeHook:
    type_ = datetime

    @staticmethod
    def from_db(value, type_):
        logging.warning("DatetimeHook.from_db()")

        if isinstance(value, datetime):
            return value
        if isinstance(value, (int, float)):
            return datetime.fromtimestamp(value)
        if isinstance(value, str):
            return datetime.fromisoformat(value)
        if isinstance(value, DatetimeMS):
            return value.as_datetime()
        raise TypeError(f"Could not convert value '{value}' to type '{type_}'.")


register_hook(converter, DatetimeHook)


class DecimalHook:
    type_ = Decimal

    @staticmethod
    def from_db(value, type_):
        if isinstance(value, Decimal):
            return value
        if isinstance(value, Decimal128):
            return value.to_decimal()
        if isinstance(value, (str, int)):
            return Decimal(value)
        if isinstance(value, float):
            return Decimal.from_float(value)
        raise TypeError(f"Could not convert value '{value}' to type '{type_}'.")

    @staticmethod
    def to_db(value):
        # Decimal values are not allowed in pymongo. Must be Decimal128.
        return Decimal128(value)


register_hook(converter, DecimalHook)


class Decimal128Hook:
    type_ = Decimal128

    @staticmethod
    def from_db(value, type_):
        if isinstance(value, Decimal128):
            return value
        elif isinstance(value, Decimal):
            return Decimal128(value)
        raise TypeError(f"Could not convert value '{value}' to type '{type_}'.")


register_hook(converter, Decimal128Hook)


# Note:
# Nothing needs to be done for Int64 since it is a subclass of int.
# Although it might be worth adding a test just to make sure that never changes.


class FrozensetHook:
    type_ = frozenset

    @staticmethod
    def from_db(value, type_):
        if isinstance(value, frozenset):
            return value
        elif isinstance(value, (list, tuple, set)):
            return frozenset(value)

    @staticmethod
    def to_db(value):
        return list(value)


register_hook(converter, FrozensetHook)


class ObjectIdHook:
    type_ = ObjectId

    @staticmethod
    def from_db(value, type_):
        return ObjectId(value)


register_hook(converter, ObjectIdHook)


class PatternHook:
    type_ = Pattern

    @staticmethod
    def from_db(value, type_):
        if isinstance(value, Pattern):
            return value
        if isinstance(value, Regex):
            return value.try_compile()
        raise TypeError(f"Could not convert value '{value}' to type '{type_}'.")


register_hook(converter, PatternHook)


class RegexHook:
    type_ = Regex

    @staticmethod
    def from_db(value, type_):
        if isinstance(value, Regex):
            return value
        elif isinstance(value, Pattern):
            return Regex.from_native(value)
        raise TypeError(f"Could not convert value '{value}' to type '{type_}'.")


register_hook(converter, RegexHook)


class SetHook:
    type_ = set

    @staticmethod
    def from_db(value, type_):
        if isinstance(value, set):
            return value
        elif isinstance(value, (list, tuple, frozenset)):
            return set(value)

    @staticmethod
    def to_db(value):
        return list(value)


register_hook(converter, SetHook)


class SONHook:
    type_ = SON

    @staticmethod
    def from_db(value, type_):
        return SON(value)


register_hook(converter, SONHook)


class UUIDHook:
    type_ = UUID

    @staticmethod
    def from_db(value, type_):
        if isinstance(value, UUID):
            return value
        elif isinstance(value, Binary):
            return value.as_uuid(value.subtype)
        elif isinstance(value, int):
            return UUID(int=value)
        elif isinstance(value, str):
            return UUID(hex=value)
        raise TypeError(f"Could not convert value '{value}' to type '{type_}'.")


register_hook(converter, UUIDHook)

from datetime import datetime
from decimal import Decimal
from re import Pattern
from uuid import UUID

from bson import Binary, DatetimeMS, Decimal128, ObjectId, Regex, SON
import cattrs

converter = cattrs.Converter()


def register_hook(converter, hook):
    if hasattr(hook, "from_db"):
        converter.register_structure_hook(hook.type_, hook.from_db)
    
    if hasattr(hook, "to_db"):
        converter.register_unstructure_hook(hook.type_, hook.to_db)


class DatetimeHook:
    type_ = datetime

    @staticmethod
    def from_db(value, type_):
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
            return Binary.as_uuid(value)
        elif isinstance(value, int):
            return UUID(int=value)
        elif isinstance(value, str):
            return UUID(hex=value)
        raise TypeError(f"Could not convert value '{value}' to type '{type_}'.")

register_hook(converter, UUIDHook)

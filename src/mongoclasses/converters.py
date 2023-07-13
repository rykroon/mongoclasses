from datetime import datetime
from decimal import Decimal
from re import Pattern
from uuid import UUID

from bson import Binary, Decimal128, ObjectId, Regex, SON
import cattrs

converter = cattrs.Converter()


# Python types


class DatetimeHook:
    @staticmethod
    def from_db(value, type_):
        if isinstance(value, datetime):
            return value
        elif isinstance(value, (int, float)):
            return datetime.fromtimestamp(value)
        if isinstance(value, str):
            return datetime.fromisoformat(value)
        raise TypeError(f"Could not convert value '{value}' to type '{type_}'.")


converter.register_structure_hook(datetime, DatetimeHook.from_db)


class DecimalHook:
    @staticmethod
    def from_db(value, type_):
        if isinstance(value, Decimal):
            return value
        elif isinstance(value, Decimal128):
            return Decimal(str(value))
        elif isinstance(value, (str, int)):
            return Decimal(value)
        elif isinstance(value, float):
            return Decimal.from_float(value)
        raise TypeError(f"Could not convert value '{value}' to type '{type_}'.")

    @staticmethod
    def to_db(value):
        return Decimal128(value)


converter.register_structure_hook(Decimal, DecimalHook.from_db)
converter.register_unstructure_hook(Decimal, DecimalHook.to_db)


class PatternHook:
    @staticmethod
    def from_db(value, type_):
        if isinstance(value, Regex):
            return value.try_compile()
        raise TypeError(f"Could not convert value '{value}' to type '{type_}'.")


converter.register_structure_hook(Pattern, PatternHook.from_db)


class UuidHook:
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


converter.register_structure_hook(UUID, UuidHook.from_db)


# bson types


class Decimal128Hook:
    @staticmethod
    def from_db(value, type_):
        if isinstance(value, Decimal128):
            return value
        raise TypeError(f"Could not convert value '{value}' to type '{type_}'.")


converter.register_structure_hook(Decimal128, Decimal128Hook.from_db)


class ObjectIdHook:
    @staticmethod
    def from_db(value, type_):
        return ObjectId(value)


converter.register_structure_hook(ObjectId, ObjectIdHook.from_db)


class RegexHook:
    @staticmethod
    def from_db(value, type_):
        if isinstance(value, Regex):
            return value


converter.register_structure_hook(Regex, RegexHook.from_db)


class SONHook:
    @staticmethod
    def from_db(value, type_):
        return SON(value)


converter.register_structure_hook(SON, SONHook.from_db)

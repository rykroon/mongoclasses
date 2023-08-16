from dataclasses import dataclass, fields, is_dataclass
from typing import Any, ClassVar, List, Literal, Union


class UpdateOperator:
    key: ClassVar[str]
    value: Any


@dataclass
class CurrentDate(UpdateOperator):
    key: ClassVar[str] = "$currentDate"
    value: Literal["timstamp", "date"] = "date"

    def __post_init__(self):
        self.value = {"$type": self.value}


@dataclass
class Inc(UpdateOperator):
    key: ClassVar[str] = "$inc"
    value: Union[int, float]


@dataclass
class Min(UpdateOperator):
    key: ClassVar[str] = "$min"
    value: Any


@dataclass
class Max(UpdateOperator):
    key: ClassVar[str] = "$max"
    value: Any


@dataclass
class Mul(UpdateOperator):
    key: ClassVar[str] = "$mul"
    value: Union[int, float]


@dataclass
class Rename(UpdateOperator):
    key: ClassVar[str] = "$rename"
    value: str


@dataclass
class Unset(UpdateOperator):
    key: ClassVar[str] = "$unset"
    value: Any = ""


@dataclass
class AddToSet(UpdateOperator):
    key: ClassVar[str] = "$addToSet"
    value: Any


@dataclass
class Pop(UpdateOperator):
    key: ClassVar[str] = "$pop"
    value: Literal[-1, 1]


@dataclass
class Pull(UpdateOperator):
    key: ClassVar[str] = "$pull"
    value: Any


@dataclass
class Push(UpdateOperator):
    key: ClassVar[str] = "$push"
    value: Any


@dataclass
class PullAll(UpdateOperator):
    key: ClassVar[str] = "$pullAll"
    value: List[Any]


def to_update_expr(obj, /, update_fields=None):
    result = {}
    return any_to_update_expr(result, None, obj)


def any_to_update_expr(result, path, obj, update_fields=None):
    if isinstance(obj, UpdateOperator):
        result.setdefault(obj.key, {})[path] = obj.value

    elif is_dataclass(obj):
        for field in fields(obj):
            db_field = field.metadata.get("mongoclasses", {}).get("db_field", field.name)
            field_path = db_field if path is None else f"{path}.{db_field}"
            v = getattr(obj, field.name)
            any_to_update_expr(result, field_path, v)

    elif isinstance(obj, (list, tuple)):
        for i, v in enumerate(obj):
            any_to_update_expr(result, f"{path}.{i}", v)

    elif isinstance(obj, dict):
        for k, v in obj.items():
            any_to_update_expr(result, f"{path}.{k}", v)

    else:
        result.setdefault("$set", {})[path] = obj

    return result

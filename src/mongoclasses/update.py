from dataclasses import dataclass, field, fields, is_dataclass, InitVar
from typing import Any, ClassVar, List, Literal, TypedDict, Union


class UpdateOperator:
    key: ClassVar[str]
    value: Any


TypeSpecification = TypedDict(
    "TypeSpecification", {"$type": Literal["timestamp", "date"]}
)

@dataclass
class CurrentDate(UpdateOperator):
    key: ClassVar[str] = "$currentDate"
    type: InitVar[Literal["timestamp", "date"]] = "date"
    value: TypeSpecification = field(init=False)

    def __post_init__(self, type) -> None:
        self.value = {"$type": type}


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


def to_update_expr(obj, /, include=None):
    return any_to_update_expr({}, None, obj, include)


def any_to_update_expr(result, path, obj, include=None):
    if path is not None and include is not None:
        parts = path.split(".")
        for i in range(len(parts)):
            p = ".".join(parts[:i+1])
            if p in include:
                break
        else:
            return result

    if isinstance(obj, UpdateOperator):
        result.setdefault(obj.key, {})[path] = obj.value

    elif is_dataclass(obj):
        for field in fields(obj):
            db_field = field.metadata.get("mongoclasses", {}).get("db_field", field.name)
            field_path = db_field if path is None else f"{path}.{db_field}"
            v = getattr(obj, field.name)
            any_to_update_expr(result, field_path, v, include)

    elif isinstance(obj, (list, tuple)):
        for i, v in enumerate(obj):
            any_to_update_expr(result, f"{path}.{i}", v, include)

    elif isinstance(obj, dict):
        for k, v in obj.items():
            any_to_update_expr(result, f"{path}.{k}", v, include)

    else:
        result.setdefault("$set", {})[path] = obj

    return result

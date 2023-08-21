from collections.abc import Mapping, Sequence
from typing import Any, Literal, TypeAlias, TypedDict

# Field Update Operators
# https://www.mongodb.com/docs/manual/reference/operator/update-field/#field-update-operators

TypeSpecification = TypedDict(
    "TypeSpecification", {"$type": Literal["date", "timestamp"]}
)

CurrentDate = TypedDict("CurrentDate", {"$currentDate": bool | TypeSpecification})

Inc = TypedDict("Inc", {"$inc": Mapping[str, int | float]})
Min = TypedDict("Min", {"$min": Mapping[str, Any]})
Max = TypedDict("Max", {"$max": Mapping[str, Any]})
Mul = TypedDict("Mul", {"$mul": Mapping[str, int | float]})
Rename = TypedDict("Rename", {"$rename": Mapping[str, str]})
Set = TypedDict("Set", {"$set": Mapping[str, Any]})
SetOnInsert = TypedDict("SetOnInsert", {"$setOnInsert": Mapping[str, Any]})
Unset = TypedDict("Unset", {"$unset": Mapping[str, Any]})

AddToSet = TypedDict("AddToSet", {"$addToSet": Mapping[str, Any]})
Pop = TypedDict("Pop", {"$pop": Mapping[str, Literal[-1, 1]]})
Pull = TypedDict("Pull", {"$pull": Mapping[str, Any]})
Push = TypedDict("Push", {"$push": Mapping[str, Any]})
PullAll = TypedDict("PullAll", {"$pullAll": Mapping[str, Sequence[Any]]})

def current_date(
    arg: Mapping[str, bool | TypeSpecification]
    | Sequence[tuple[str, bool | TypeSpecification]]
    | None = None,
    /,
    **kwargs: bool | TypeSpecification,
) -> CurrentDate:
    pass

def inc(
    arg: Mapping[str, int | float] | Sequence[tuple[str, int | float]] | None = None,
    /,
    **kwargs: int | float,
) -> Inc:
    pass

def min(
    arg: Mapping[str, Any] | Sequence[tuple[str, Any]] | None = None,
    /,
    **kwargs: Any,
) -> Min:
    pass

def max(
    arg: Mapping[str, Any] | Sequence[tuple[str, Any]] | None = None,
    /,
    **kwargs: Any,
) -> Max:
    pass

def mul(
    arg: Mapping[str, int | float] | Sequence[tuple[str, int | float]] | None = None,
    /,
    **kwargs: int | float,
) -> Mul:
    pass

def rename(
    arg: Mapping[str, str] | Sequence[tuple[str, str]] | None = None,
    /,
    **kwargs: str,
) -> Rename:
    pass

def set(
    arg: Mapping[str, Any] | Sequence[tuple[str, Any]] | None = None,
    /,
    **kwargs: Any,
) -> Set:
    pass

def set_on_insert(
    arg: Mapping[str, Any] | Sequence[tuple[str, Any]] | None = None,
    /,
    **kwargs: Any,
) -> SetOnInsert:
    pass

def unset(
    arg: Mapping[str, Any] | Sequence[tuple[str, Any]] | None = None,
    /,
    **kwargs: Any,
) -> Unset:
    pass

# Array Update Operators
# https://www.mongodb.com/docs/manual/reference/operator/update-array/#array-update-operators

def add_to_set(
    arg: Mapping[str, Any] | Sequence[tuple[str, Any]] | None = None,
    /,
    **kwargs: Any,
) -> AddToSet:
    pass

def pop(
    arg: Mapping[str, Literal[-1, 1]]
    | Sequence[tuple[str, Literal[-1, 1]]]
    | None = None,
    /,
    **kwargs: Literal[-1, 1],
) -> Pop:
    pass

def pull(
    arg: Mapping[str, Any] | Sequence[tuple[str, Any]] | None = None,
    /,
    **kwargs: Any,
) -> Pull:
    pass

def push(
    arg: Mapping[str, Any] | Sequence[tuple[str, Any]] | None = None,
    /,
    **kwargs: Any,
) -> Push:
    pass

def pull_all(
    arg: Mapping[str, Sequence[Any]]
    | Sequence[tuple[str, Sequence[Any]]]
    | None = None,
    /,
    **kwargs: Sequence[Any],
) -> PullAll:
    pass

# Update Operator Modifiers
# https://www.mongodb.com/docs/manual/reference/operator/update-array/#update-operator-modifiers

def each(values: Sequence[Any]):
    pass

def position(num: int, /):
    pass

def slice(num: int, /):
    pass

def sort(sort_specification: Literal[-1, 1] | Mapping[str, Literal[-1, 1]], /):
    pass

# Bitwise Update Operators
# https://www.mongodb.com/docs/manual/reference/operator/update-bitwise/#bitwise-update-operator

and_or_xor: TypeAlias = Literal["and", "or", "xor"]

def bit(
    arg: Mapping[str, Mapping[and_or_xor, int]]
    | Sequence[tuple[str, Mapping[and_or_xor, int]]]
    | None = None,
    /,
    **kwargs,
):
    pass

from dataclasses import dataclass, fields, is_dataclass
from typing import Any, Literal, Union

from .serialization import to_document


class UpdateOperator:
    pass


@dataclass
class CurrentDate(UpdateOperator):
    type_specification: Literal["timstamp", "date"] = "date"


@dataclass
class Inc(UpdateOperator):
    amount: Union[int, float]


@dataclass
class Min(UpdateOperator):
    value: Any


@dataclass
class Max(UpdateOperator):
    value: Any


@dataclass
class Mul(UpdateOperator):
    number: Union[int, float]


@dataclass
class Unset:
    pass


class UpdateExpr(dict):

    @property
    def current_date(self):
        return self.setdefault("$currentDate", {})

    @property
    def inc(self):
        return self.setdefault("$inc", {})

    @property
    def min(self):
        return self.setdefault("$min", {})

    @property
    def max(self):
        return self.setdefault("$max", {})

    @property
    def mul(self):
        return self.setdefault("$mul", {})

    @property
    def set(self):
        return self.setdefault("$set", {})
    
    @property
    def unset(self):
        return self.setdefault("$unset", {})


def recursive_update(mapping, *new_mappings):
    for new_mapping in new_mappings:
        for k, v in new_mapping.items():
            if k in mapping and isinstance(mapping[k], dict) and isinstance(v, dict):
                mapping[k] = recursive_update(mapping[k], v)
            else:
                mapping[k] = v
    return mapping


def to_update_expr(obj, /, update_fields=None):
    result = UpdateExpr()
    return any_to_update_expr(result, None, obj)


def any_to_update_expr(result, path, obj, update_fields=None):
    if isinstance(obj, UpdateOperator):
        if isinstance(obj, CurrentDate):
            result.current_date[path] = {"$type": obj.type_specification}

        elif isinstance(obj, Inc):
            result.inc[path] = obj.amount

        elif isinstance(obj, Min):
            result.min[path] = obj.value

        elif isinstance(obj, Max):
            result.max[path] = obj.value

        elif isinstance(obj, Mul):
            result.mul[path] = obj.number

        elif isinstance(obj, Unset):
            result.unset[path] = {path: ""}

    elif is_dataclass(obj):
        for fld in fields(obj):
            field_name = fld.metadata.get("mongoclasses", {}).get("db_field", fld.name)
            field_path = field_name if path is None else f"{path}.{field_name}"
            v = getattr(obj, fld.name)
            any_to_update_expr(result, field_path, v)

    elif isinstance(obj, (list, tuple)):
        for i, v in enumerate(obj):
            any_to_update_expr(result, f"{path}.{i}", v)

    elif isinstance(obj, dict):
        for k, v in obj.items():
            any_to_update_expr(result, f"{path}.{k}", v)

    else:
        result.set[path] = obj

    return result

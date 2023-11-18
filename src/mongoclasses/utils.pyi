from dataclasses import dataclass, Field
from typing import Any
from typing_extensions import TypeGuard

from .types import DataclassInstance, MongoclassInstance

@dataclass(frozen=True)
class FieldInfo:
    db_field: str | None = None
    unique: bool = False

def get_field_info(field: Field[Any]) -> FieldInfo | None:
    pass

def get_field_name(field: Field[Any]) -> str:
    pass

def get_id_field(cls: type[DataclassInstance]) -> Field[Any]:
    pass

def set_id(obj: MongoclassInstance, id: Any) -> None:
    pass

def get_id(obj: MongoclassInstance) -> Any:
    pass

def resolve_type(t: type) -> type | list[type]:
    pass

def is_union(t: type) -> bool:
    pass

def is_dataclass_type(obj: Any) -> TypeGuard[type[DataclassInstance]]:
    pass

def is_dataclass_instance(obj: Any) -> TypeGuard[DataclassInstance]:
    pass

def is_mongoclass(
    obj: Any,
) -> TypeGuard[MongoclassInstance | type[MongoclassInstance]]:
    pass

def is_mongoclass_type(obj: Any) -> TypeGuard[type[MongoclassInstance]]:
    pass

def is_mongoclass_instance(obj: Any) -> TypeGuard[MongoclassInstance]:
    pass


from typing import Any
from .mongoclasses import MongoclassInstance

def to_update_expr(
    obj: MongoclassInstance, /, include: list[str] | None=None
) -> dict[str, Any]:
    pass

def any_to_update_expr(
    result: dict[str, Any], path: str | None, obj: Any, include: list[str] | None=None
) -> dict[str, Any]:
    pass

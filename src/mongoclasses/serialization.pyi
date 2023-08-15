from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from _typeshed import DataclassInstance


def to_document(obj: DataclassInstance) -> dict[str, Any]: pass
def from_document(
    cls: type[DataclassInstance], data:dict[str, Any]
) -> DataclassInstance: pass

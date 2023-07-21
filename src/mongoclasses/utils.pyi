from dataclasses import Field
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from _typeshed import DataclassInstance


def _get_id_field(dcls: DataclassInstance) -> Field | None: pass
def _get_db_name(field: Field) -> str: pass

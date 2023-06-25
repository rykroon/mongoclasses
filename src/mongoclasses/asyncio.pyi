from typing import Any, Callable, TypeAlias, TYPE_CHECKING
from pymongo.results import DeleteResult, InsertOneResult, UpdateResult
from .dataclass import MongoclassInstance, Data

if TYPE_CHECKING:
    from _typeshed import DataclassInstance

DictFactory: TypeAlias = Callable[[list[tuple[str, Any]]], Data]


async def insert_one(
    obj: MongoclassInstance, /, dict_factory: DictFactory
) -> InsertOneResult:
    ...


async def update_one(
    obj: MongoclassInstance, /, dict_factory: DictFactory
) -> UpdateResult:
    ...


async def delete_one(obj: MongoclassInstance, /) -> DeleteResult:
    ...


async def find_one(
    cls: type[MongoclassInstance],
    /,
    query: Data,
    fromdict: Callable[[type[DataclassInstance], Data], DataclassInstance],
) -> MongoclassInstance | None:
    ...
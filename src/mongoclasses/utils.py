from dataclasses import dataclass, fields, is_dataclass, Field
from typing import Any, List, Optional, Type, TypeVar, Union
from typing_extensions import Annotated, get_origin

from pymongo import IndexModel
from pymongo.collection import Collection
from pymongo.database import Database
from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorCollection

from .types import DataclassInstance, MongoclassInstance


DT = TypeVar("DT", bound=DataclassInstance)
MT = TypeVar("MT", bound=MongoclassInstance)


@dataclass(frozen=True)
class MongoClassConfig:
    collection: Union[Collection, AsyncIOMotorCollection]
    id_field: Field
    indexes: List[IndexModel]


@dataclass(frozen=True)
class FieldMeta:
    db_field: Optional[str] = None
    unique: bool = False


def mongoclass(
    *,
    db: Union[Database, AsyncIOMotorDatabase],
    collection_name: Optional[str] = None,
    indexes: Optional[List[IndexModel]] = None,
):
    if indexes is None:
        indexes = []

    def decorator(cls: Type[DT]) -> Type[MT]:
        return _process_class(cls, db, collection_name, indexes)

    return decorator


def _process_class(
    cls: Type[DT],
    db: Union[Database, AsyncIOMotorDatabase],
    collection_name: Optional[str],
    indexes: List[IndexModel],
) -> Type[MT]:
    if not is_dataclass(cls):
        raise TypeError(f"Class {cls} is not a dataclass")

    if collection_name is None:
        collection_name = cls.__name__.lower()
    collection = db[collection_name]

    id_field = None
    for field in fields(cls):
        if get_field_name(field) == "_id":
            id_field = field

        # Check for indexes

    if id_field is None:
        raise TypeError(f"Class {cls} has no _id field")

    config = MongoClassConfig(
        collection=collection,
        id_field=id_field,
        indexes=indexes,
    )
    setattr(cls, "__mongoclass_config__", config)
    return cls


def get_field_name(field: Field) -> str:
    field_meta = get_field_meta(field)

    if field_meta is not None and field_meta.db_field is not None:
        return field_meta.db_field

    return field.name


def get_field_meta(field: Field) -> Optional[FieldMeta]:
    if get_origin(field.type) is not Annotated:
        return None

    for annotation in field.type.__metadata__:
        if isinstance(annotation, FieldMeta):
            return annotation

    return None


def get_id(obj: Any, /) -> Any:
    config = obj.__mongoclass_config__
    return getattr(obj, config.id_field.name)


def set_id(obj: Any, /, value: Any) -> None:
    config = obj.__mongoclass_config__
    setattr(obj, config.id_field.name, value)


def get_collection(obj: Any, /) -> Union[Collection, AsyncIOMotorCollection]:
    config = obj.__mongoclass_config__
    return config.collection


def is_mongoclass(obj: Any, /) -> bool:
    cls = obj if isinstance(obj, type) else type(obj)
    return hasattr(cls, "__mongoclass_config__")


def _is_mongoclass_instance(obj: Any, /) -> bool:
    return hasattr(type(obj), "__mongoclass_config__")

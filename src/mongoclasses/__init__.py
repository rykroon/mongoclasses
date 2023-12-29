from dataclasses import dataclass, fields, is_dataclass, Field
from typing import (
    Any,
    Callable,
    ClassVar,
    Dict,
    Iterable,
    List,
    Literal,
    Optional,
    Protocol,
    Tuple,
    Type,
    TypeVar,
    Union,
)
from typing_extensions import Annotated, TypeGuard, get_origin

import cattrs
from cattrs.gen import make_dict_structure_fn, make_dict_unstructure_fn, override
from cattrs.preconf.bson import make_converter
from motor.motor_asyncio import (
    AsyncIOMotorCollection,
    AsyncIOMotorCursor,
    AsyncIOMotorDatabase,
)
from pymongo import IndexModel
from pymongo.collection import Collection
from pymongo.cursor import Cursor
from pymongo.database import Database
from pymongo.results import InsertOneResult, UpdateResult, DeleteResult


@dataclass(frozen=True)
class MongoClassConfig:
    collection: Union[Collection, AsyncIOMotorCollection]
    id_field: Field
    indexes: Tuple[IndexModel, ...]
    converter: cattrs.Converter


class DataclassInstance(Protocol):
    __dataclass_fields__: ClassVar[Dict[str, Field]]


class MongoclassInstance(DataclassInstance):
    __mongoclass_config__: ClassVar[MongoClassConfig]


T = TypeVar("T", bound=MongoclassInstance)


class DeveloperError(Exception):
    """
    This exception is raised when the developer has made a mistake.
    """
    pass


@dataclass(frozen=True)
class FieldMeta:
    """
    Metadata for mongoclass fields.
    """

    db_field: Optional[str] = None
    unique: bool = False


def mongoclass(
    cls: Optional[Type[Any]] = None,
    /,
    *,
    db: Union[Database, AsyncIOMotorDatabase, None] = None,
    collection_name: Optional[str] = None,
    indexes: Optional[List[IndexModel]] = None,
    **dataclass_kwargs: Any,
) -> Union[Type[MongoclassInstance], Callable[[Type[Any]], Type[MongoclassInstance]]]:
    """
    Converts a class into a mongoclass.

    Parameters:
        db: A pymongo database object.
        collection_name: The name of the collection to use.
        indexes: A list of pymongo `IndexModel` objects.
        **dataclass_kwargs: Keyword arguments to pass to the `dataclass` decorator.

    Raises:
        DeveloperError: If the class does not have an _id field.
        DeveloperError: If the class is not a mongoclass and no database is specified.

    Returns:
        A decorator that converts a class into a mongoclass.
    """
    def wrap(cls: Type[Any]) -> Type[MongoclassInstance]:
        return _process_class(cls, db, collection_name, indexes, dataclass_kwargs)

    if cls is None:
        return wrap

    return wrap(cls)


def _process_class(
    cls: Type[Any],
    db: Union[Database, AsyncIOMotorDatabase, None],
    collection_name: Optional[str],
    indexes: Optional[List[IndexModel]],
    dataclass_kwargs: Dict[str, Any],
) -> Type[MongoclassInstance]:
    if not is_dataclass(cls) or dataclass_kwargs:
        cls = dataclass(**dataclass_kwargs)(cls)

    if collection_name is None:
        collection_name = cls.__name__.lower()

    if db is not None:
        collection = db[collection_name]

    elif is_mongoclass(cls):
        parent_collection = get_collection(cls)
        collection = parent_collection[collection_name]

    else:
        raise DeveloperError("Must specify a database.")
    
    if indexes is None:
        indexes = []

    id_field = None
    overrides = {}
    for field in fields(cls):
        field_name = _get_field_name(field)
        if field_name == "_id":
            id_field = field

        if field_name != field.name:
            overrides[field.name] = override(rename=field_name)

        # Check for indexes
        field_meta = _get_field_meta(field)
        if field_meta is not None and field_meta.unique is True:
            indexes.append(IndexModel(field_name, unique=True))

    if id_field is None:
        raise DeveloperError(f"Class {cls} has no _id field")

    converter = make_converter()
    if overrides:
        unstruct_func = make_dict_unstructure_fn(cls, converter, **overrides)
        struct_func = make_dict_structure_fn(cls, converter, **overrides)
        converter.register_unstructure_hook(cls, unstruct_func)
        converter.register_structure_hook(cls, struct_func)

    config = MongoClassConfig(
        collection=collection,
        id_field=id_field,
        indexes=tuple(indexes),
        converter=converter,
    )
    setattr(cls, "__mongoclass_config__", config)
    return cls


def _get_field_name(field: Field) -> str:
    field_meta = _get_field_meta(field)

    if field_meta is not None and field_meta.db_field is not None:
        return field_meta.db_field

    return field.name


def _get_field_meta(field: Field) -> Optional[FieldMeta]:
    if get_origin(field.type) is not Annotated:
        return None

    for annotation in field.type.__metadata__:
        if isinstance(annotation, FieldMeta):
            return annotation

    return None


def get_id(obj: MongoclassInstance, /) -> Any:
    try:
        config = type(obj).__mongoclass_config__
    except AttributeError:
        raise TypeError("Object must be a mongoclass instance.")

    return getattr(obj, config.id_field.name)


def set_id(obj: MongoclassInstance, /, value: Any) -> None:
    try:
        config = type(obj).__mongoclass_config__
    except AttributeError:
        raise TypeError("Object must be a mongoclass instance.")

    setattr(obj, config.id_field.name, value)


def get_collection(
    obj: Union[Type[MongoclassInstance], MongoclassInstance], /
) -> Union[Collection, AsyncIOMotorCollection]:
    """
    Returns the collection associated with the mongoclass.
    """
    try:
        config = obj.__mongoclass_config__
    except AttributeError:
        raise TypeError("Object must be a mongoclass.")

    return config.collection


def get_converter(
    obj: Union[Type[MongoclassInstance], MongoclassInstance], /
) -> cattrs.Converter:
    """
    Returns the converter associated with the mongoclass.
    """
    try:
        config = obj.__mongoclass_config__
    except AttributeError:
        raise TypeError("Object must be a mongoclass.")

    return config.converter


def is_mongoclass(
    obj: Any, /
) -> TypeGuard[Union[Type[MongoclassInstance], MongoclassInstance]]:
    """
    Returns True if the object is a mongoclass.
    """
    cls = obj if isinstance(obj, type) else type(obj)
    return hasattr(cls, "__mongoclass_config__")


def to_document(obj: MongoclassInstance, /) -> Dict[str, Any]:
    """
    Converts a mongoclass instance into a dictionary.
    """
    converter = get_converter(type(obj))
    return converter.unstructure(obj)


def from_document(cls: Type[T], /, data: Dict[str, Any]) -> T:
    """
    Converts a dictionary into a mongoclass instance.
    """
    converter = get_converter(cls)
    return converter.structure(data, cls)


def insert_one(obj: MongoclassInstance, /) -> InsertOneResult:
    """
    Inserts the object into the database.

    Parameters:
        obj: A mongoclass instance.

    Returns:
        A pymongo `InsertOneResult` object.
    """
    document = to_document(obj)
    collection = get_collection(obj)
    result = collection.insert_one(document)
    set_id(obj, result.inserted_id)
    return result


async def ainsert_one(obj: MongoclassInstance, /) -> InsertOneResult:
    document = to_document(obj)
    collection = get_collection(obj)
    result = await collection.insert_one(document)
    assert isinstance(result, InsertOneResult)
    set_id(obj, result.inserted_id)
    return result


ainsert_one.__doc__ = insert_one.__doc__


def update_one(obj: MongoclassInstance, update: Dict[str, Any], /) -> UpdateResult:
    """
    Updates the object in the database.

    Parameters:
        obj: A mongoclass instance.
        update: An update document.

    Returns:
        A pymongo `UpdateResult` object.
    """
    collection = get_collection(obj)
    return collection.update_one(filter={"_id": get_id(obj)}, update=update)


async def aupdate_one(
    obj: MongoclassInstance, update: Dict[str, Any], /
) -> UpdateResult:
    collection = get_collection(obj)
    result = await collection.update_one(filter={"_id": get_id(obj)}, update=update)
    assert isinstance(result, UpdateResult)
    return result


aupdate_one.__doc__ = update_one.__doc__


def replace_one(obj: MongoclassInstance, /, upsert: bool = False) -> UpdateResult:
    """
    Replaces the object in the database.

    Parameters:
        obj: A mongoclass instance.
        upsert: If True, will insert the document if it does not already exist.

    Returns:
        A pymongo `UpdateResult` object.
    """
    document = to_document(obj)
    collection = get_collection(obj)
    return collection.replace_one(
        filter={"_id": get_id(obj)}, replacement=document, upsert=upsert
    )


async def areplace_one(
    obj: MongoclassInstance, /, upsert: bool = False
) -> UpdateResult:
    document = to_document(obj)
    collection = get_collection(obj)
    result = await collection.replace_one(
        filter={"_id": get_id(obj)}, replacement=document, upsert=upsert
    )
    assert isinstance(result, UpdateResult)
    return result


areplace_one.__doc__ = replace_one.__doc__


def delete_one(obj: MongoclassInstance, /) -> DeleteResult:
    """
    Deletes the object from the database.

    Parameters:
        obj: A mongoclass instance.

    Returns:
        A pymongo `DeleteResult` object.
    """
    collection = get_collection(obj)
    return collection.delete_one({"_id": get_id(obj)})


async def adelete_one(obj: MongoclassInstance, /) -> DeleteResult:
    collection = get_collection(obj)
    result = await collection.delete_one({"_id": get_id(obj)})
    assert isinstance(result, DeleteResult)
    return result


adelete_one.__doc__ = delete_one.__doc__


def find_one(cls: Type[T], /, filter: Optional[Dict[str, Any]] = None) -> Optional[T]:
    """
    Return a single instance that matches the query or None.

    Parameters:
        cls: A mongoclass type.
        filter: A dictionary specifying the query to be performed.

    Returns:
        A mongoclass instance or None.
    """
    collection = get_collection(cls)
    document = collection.find_one(filter=filter)
    if document is None:
        return None
    return from_document(cls, document)


async def afind_one(
    cls: Type[T], /, filter: Optional[Dict[str, Any]] = None
) -> Optional[T]:
    collection = get_collection(cls)
    document = await collection.find_one(filter=filter)
    if document is None:
        return None
    return from_document(cls, document)


afind_one.__doc__ = find_one.__doc__


def find(
    cls: Type[MongoclassInstance],
    /,
    filter: Optional[Dict[str, Any]] = None,
    skip: int = 0,
    limit: int = 0,
    sort: Optional[List[Tuple[str, Literal[-1, 1]]]] = None,
) -> Union[Cursor, AsyncIOMotorCursor]:
    """
    Performs a query on the collection associated with the mongoclass.

    Parameters:
        cls: A mongoclass.
        filter: A query document that selects which documents to include in the result set.
        skip: The number of documents to omit from the start of the result set.
        limit: The maximum number of results to return.
        sort: A list of (key, direction) pairs.

    Returns:
        A MongoDB cursor.
    """
    collection = get_collection(cls)
    return collection.find(filter=filter, skip=skip, limit=limit, sort=sort)


def iter_objects(cls: Type[T], cursor: Cursor) -> Iterable[T]:
    for document in cursor:
        yield from_document(cls, document)


async def aiter_objects(cls: Type[T], cursor: AsyncIOMotorCursor) -> Iterable[T]:
    async for document in cursor:
        yield from_document(cls, document)


def create_indexes(cls: Type[MongoclassInstance], /) -> List[str]:
    """
    Creates the indexes specified by the mongoclass.

    Parameters:
        cls: A mongoclass.

    Returns:
        A list of index names.
    """
    collection = get_collection(cls)
    return collection.create_indexes(list(cls.__mongoclass_config__.indexes))


async def acreate_indexes(cls: Type[MongoclassInstance], /) -> List[str]:
    collection = get_collection(cls)
    return await collection.create_indexes(list(cls.__mongoclass_config__.indexes))


acreate_indexes.__doc__ = create_indexes.__doc__

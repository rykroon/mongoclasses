from typing import (
    Any,
    Dict,
    Iterable,
    List,
    Literal,
    Optional,
    Tuple,
    Type,
    TypeVar,
    Union,
)

from motor.motor_asyncio import AsyncIOMotorCursor
from pymongo import IndexModel
from pymongo.cursor import Cursor
from pymongo.results import InsertOneResult, UpdateResult, DeleteResult

from .serialization import to_document, from_document
from .utils import (
    get_collection,
    get_id,
    set_id,
    is_mongoclass,
    _is_mongoclass_instance,
)
from .types import MongoclassInstance


T = TypeVar("T", bound=MongoclassInstance)


def insert_one(obj: T, /) -> InsertOneResult:
    """
    Inserts the object into the database.

    Parameters:
        obj: A mongoclass instance.

    Raises:
        TypeError: If the object is not a mongoclass instance.

    Returns:
        A pymongo `InsertOneResult` object.
    """
    if not _is_mongoclass_instance(obj):
        raise TypeError("Not a mongoclass instance.")

    document = to_document(obj)
    collection = get_collection(obj)
    result = collection.insert_one(document)
    set_id(obj, result.inserted_id)
    return result


async def ainsert_one(obj: T, /) -> InsertOneResult:
    if not _is_mongoclass_instance(obj):
        raise TypeError("Not a mongoclass instance.")

    document = to_document(obj)
    collection = get_collection(obj)
    result = await collection.insert_one(document)
    assert isinstance(result, InsertOneResult)
    set_id(obj, result.inserted_id)
    return result


ainsert_one.__doc__ = insert_one.__doc__


def update_one(obj: T, update: Dict[str, Any], /) -> UpdateResult:
    """
    Updates the object in the database.

    Parameters:
        obj: A mongoclass instance.
        update: An update document.

    Raises:
        TypeError: If the object is not a mongoclass instance.

    Returns:
        A pymongo `UpdateResult` object.
    """
    if not _is_mongoclass_instance(obj):
        raise TypeError("Not a mongoclass instance.")

    collection = get_collection(obj)
    return collection.update_one(filter={"_id": get_id(obj)}, update=update)


async def aupdate_one(obj: T, update: Dict[str, Any], /) -> UpdateResult:
    if not _is_mongoclass_instance(obj):
        raise TypeError("Not a mongoclass instance.")

    collection = get_collection(obj)
    result = await collection.update_one(filter={"_id": get_id(obj)}, update=update)
    assert isinstance(result, UpdateResult)
    return result


aupdate_one.__doc__ = update_one.__doc__


def replace_one(obj: T, /, upsert: bool = False) -> UpdateResult:
    """
    Replaces the object in the database.

    Parameters:
        obj: A mongoclass instance.
        upsert: If True, will insert the document if it does not already exist.

    Raises:
        TypeError: If the object is not a mongoclass instance.

    Returns:
        A pymongo `UpdateResult` object.
    """
    if not _is_mongoclass_instance(obj):
        raise TypeError("Not a mongoclass instance.")

    document = to_document(obj)
    collection = get_collection(obj)
    return collection.replace_one(
        filter={"_id": get_id(obj)}, replacement=document, upsert=upsert
    )


async def areplace_one(obj: T, /, upsert: bool = False) -> UpdateResult:
    if not _is_mongoclass_instance(obj):
        raise TypeError("Not a mongoclass instance.")

    document = to_document(obj)
    collection = get_collection(obj)
    result = await collection.replace_one(
        filter={"_id": get_id(obj)}, replacement=document, upsert=upsert
    )
    assert isinstance(result, UpdateResult)
    return result


areplace_one.__doc__ = replace_one.__doc__


def delete_one(obj: T, /) -> DeleteResult:
    """
    Deletes the object from the database.

    Parameters:
        obj: A mongoclass instance.

    Raises:
        TypeError: If the object is not a mongoclass instance.

    Returns:
        A pymongo `DeleteResult` object.
    """
    if not _is_mongoclass_instance(obj):
        raise TypeError("Not a mongoclass instance.")

    collection = get_collection(obj)
    return collection.delete_one({"_id": get_id(obj)})


async def adelete_one(obj: T, /) -> DeleteResult:
    if not _is_mongoclass_instance(obj):
        raise TypeError("Not a mongoclass instance.")

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

    Raises:
        TypeError: If the class is not a mongoclass.

    Returns:
        A mongoclass instance or None.
    """
    if not is_mongoclass(cls):
        raise TypeError("Not a mongoclass.")

    collection = get_collection(cls)
    document = collection.find_one(filter=filter)
    if document is None:
        return None
    return from_document(cls, document)


async def afind_one(
    cls: Type[T], /, filter: Optional[Dict[str, Any]] = None
) -> Optional[T]:
    if not is_mongoclass(cls):
        raise TypeError("Not a mongoclass.")

    collection = get_collection(cls)
    document = await collection.find_one(filter=filter)
    if document is None:
        return None
    return from_document(cls, document)


afind_one.__doc__ = find_one.__doc__


def find(
    cls: Type[T],
    /,
    filter: Optional[Dict[str, Any]] = None,
    skip: int = 0,
    limit: int = 0,
    sort: Optional[List[Tuple[str, Literal[-1, 1]]]] = None,
) -> Union[Cursor, AsyncIOMotorCursor]:
    """
    Performs a query on the mongoclass.

    Parameters:
        cls: A mongoclass.
        filter: A dictionary specifying the query to be performed.
        skip: The number of documents to omit from the start of the result set.
        limit: The maximum number of results to return.
        sort: A list of fields to sort by. If a field is prepended with a negative \
            sign it will be sorted in descending order. Otherwise ascending.

    Raises:
        TypeError: If the class is not a Mongoclass type.

    Returns:
        A `Cursor` object if the mongoclass's collection is synchronous or an \
            `AsyncCursor` object if the collection is asynchronous.
    """
    if not is_mongoclass(cls):
        raise TypeError("Not a mongoclass.")

    collection = get_collection(cls)
    return collection.find(filter=filter, skip=skip, limit=limit, sort=sort)


def iter_objects(cls: Type[T], cursor: Cursor) -> Iterable[T]:
    for document in cursor:
        yield from_document(cls, document)


async def aiter_objects(cls: Type[T], cursor: AsyncIOMotorCursor) -> Iterable[T]:
    async for document in cursor:
        yield from_document(cls, document)


def create_indexes(cls: Type[T], /) -> None:
    """
    Creates the indexes specified by the mongoclass.

    Parameters:
        cls: A mongoclass.

    Raises:
        TypeError: If the class is not a mongoclass.
    """
    if not is_mongoclass(cls):
        raise TypeError("Not a mongoclass.")

    pass

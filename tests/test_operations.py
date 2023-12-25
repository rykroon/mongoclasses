import dataclasses as dc

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCursor
from pymongo import MongoClient
from pymongo.cursor import Cursor
import pytest
import pytest_asyncio
from typing_extensions import Annotated


from mongoclasses import (
    acreate_indexes,
    ainsert_one,
    afind_one,
    aupdate_one,
    areplace_one,
    adelete_one,
    mongoclass,
    create_indexes,
    insert_one,
    find_one,
    update_one,
    replace_one,
    delete_one,
    find,
    iter_objects,
    aiter_objects,
    FieldMeta,
)


@pytest.fixture
def client():
    return MongoClient()


@pytest.fixture
def async_client():
    return AsyncIOMotorClient()


@pytest.fixture
def database(client):
    client.drop_database("test_database")
    return client.test_database


@pytest_asyncio.fixture
async def async_database(async_client):
    await async_client.drop_database("test_database")
    return async_client.test_database


def test_insert_one(database):
    @mongoclass(db=database)
    class Foo:
        _id: ObjectId = dc.field(default_factory=ObjectId)

    foo = Foo()
    insert_one(foo)
    assert database.foo.find_one({"_id": foo._id}) is not None


@pytest.mark.asyncio
async def test_ainsert_one(async_database):
    @mongoclass(db=async_database)
    class Foo:
        _id: ObjectId = dc.field(default_factory=ObjectId)

    foo = Foo()
    await ainsert_one(foo)
    assert await async_database.foo.find_one({"_id": foo._id}) is not None


def test_update_one(database):
    @mongoclass(db=database)
    class Foo:
        _id: ObjectId = dc.field(default_factory=ObjectId)
        bar: str = ""

    foo = Foo()
    insert_one(foo)
    update_one(foo, {"$set": {"bar": "baz"}})
    assert database.foo.find_one({"_id": foo._id})["bar"] == "baz"


@pytest.mark.asyncio
async def test_aupdate_one(async_database):
    @mongoclass(db=async_database)
    class Foo:
        _id: ObjectId = dc.field(default_factory=ObjectId)
        bar: str = ""

    foo = Foo()
    await ainsert_one(foo)
    await aupdate_one(foo, {"$set": {"bar": "baz"}})

    document = await async_database.foo.find_one({"_id": foo._id})
    assert document is not None
    assert document["bar"] == "baz"


def test_replace_one(database):
    @mongoclass(db=database)
    class Foo:
        _id: ObjectId = dc.field(default_factory=ObjectId)
        bar: str = ""

    foo = Foo()
    insert_one(foo)
    foo.bar = "baz"
    replace_one(foo)
    document = database.foo.find_one({"_id": foo._id})
    assert document is not None
    assert document["bar"] == "baz"


@pytest.mark.asyncio
async def test_areplace_one(async_database):
    @mongoclass(db=async_database)
    class Foo:
        _id: ObjectId = dc.field(default_factory=ObjectId)
        bar: str = ""

    foo = Foo()
    await ainsert_one(foo)
    foo.bar = "baz"
    await areplace_one(foo)
    document = await async_database.foo.find_one({"_id": foo._id})
    assert document is not None
    assert document["bar"] == "baz"


def test_delete_one(database):
    @mongoclass(db=database)
    class Foo:
        _id: ObjectId = dc.field(default_factory=ObjectId)

    foo = Foo()
    insert_one(foo)
    delete_one(foo)
    assert database.foo.find_one({"_id": foo._id}) is None


@pytest.mark.asyncio
async def test_adelete_one(async_database):
    @mongoclass(db=async_database)
    class Foo:
        _id: ObjectId = dc.field(default_factory=ObjectId)

    foo = Foo()
    await ainsert_one(foo)
    await adelete_one(foo)
    assert await async_database.foo.find_one({"_id": foo._id}) is None


def test_find_one(database):
    @mongoclass(db=database)
    class Foo:
        _id: ObjectId = dc.field(default_factory=ObjectId)

    foo = Foo()
    insert_one(foo)
    assert find_one(Foo, {"_id": foo._id}) == foo

    # test with no result.
    assert find_one(Foo, {"_id": ObjectId()}) is None


@pytest.mark.asyncio
async def test_afind_one(async_database):
    @mongoclass(db=async_database)
    class Foo:
        _id: ObjectId = dc.field(default_factory=ObjectId)

    foo = Foo()
    await ainsert_one(foo)
    assert await afind_one(Foo, {"_id": foo._id}) == foo

    # test with no result.
    assert await afind_one(Foo, {"_id": ObjectId()}) is None


def test_find(database):
    @mongoclass(db=database)
    class Foo:
        _id: ObjectId = dc.field(default_factory=ObjectId)

    cursor = find(Foo, {"_id": ObjectId()})
    assert isinstance(cursor, Cursor)


def test_find_async(async_database):
    @mongoclass(db=async_database)
    class Foo:
        _id: ObjectId = dc.field(default_factory=ObjectId)

    cursor = find(Foo, {"_id": ObjectId()})
    assert isinstance(cursor, AsyncIOMotorCursor)


def test_iter_objects(database):
    @mongoclass(db=database)
    class Foo:
        _id: ObjectId = dc.field(default_factory=ObjectId)

    foo = Foo()
    insert_one(foo)
    cursor = find(Foo, {"_id": foo._id})

    for obj in iter_objects(Foo, cursor):
        assert isinstance(obj, Foo)


@pytest.mark.asyncio
async def test_aiter_objects(async_database):
    @mongoclass(db=async_database)
    class Foo:
        _id: ObjectId = dc.field(default_factory=ObjectId)

    foo = Foo()
    await ainsert_one(foo)
    cursor = find(Foo, {"_id": foo._id})

    async for obj in aiter_objects(Foo, cursor):
        assert isinstance(obj, Foo)


def test_create_indexes(database):
    @mongoclass(db=database)
    class Foo:
        _id: ObjectId = dc.field(default_factory=ObjectId)
        name: Annotated[str, FieldMeta(unique=True)] = ""

    assert create_indexes(Foo) == ["name_1"]


@pytest.mark.asyncio
async def test_acreate_indexes(async_database):
    @mongoclass(db=async_database)
    class Foo:
        _id: ObjectId = dc.field(default_factory=ObjectId)
        name: Annotated[str, FieldMeta(unique=True)] = ""

    assert await acreate_indexes(Foo) == ["name_1"]

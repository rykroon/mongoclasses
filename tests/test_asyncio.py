from dataclasses import dataclass, field
from typing import ClassVar

from bson import ObjectId
import pytest
import pytest_asyncio
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection

from mongoclasses import find
from mongoclasses.asyncio import (
    delete_one, find_one, insert_one, replace_one, update_one
)

from mongoclasses.update import Inc


@pytest.fixture
def client():
    return AsyncIOMotorClient()


@pytest_asyncio.fixture(autouse=True)
async def drop_database(client):
    await client.drop_database("test")


@pytest.fixture
def Foo(client):
    @dataclass
    class Foo:
        collection: ClassVar[AsyncIOMotorCollection] = client["test"]["foo"]
        _id: ObjectId = field(default_factory=ObjectId)
        x: int = 0
        y: int = 0
        z: int = 0

    return Foo


@pytest.mark.asyncio
async def test_insert_one_without_id(Foo):
    f = Foo()
    await insert_one(f)

    assert f._id is not None
    assert await Foo.collection.find_one(f._id) is not None


@pytest.mark.asyncio
async def test_insert_one_with_id(Foo):
    # test scenario where an _id is generated before insertion.
    object_id = ObjectId()
    f = Foo(_id=object_id)
    await insert_one(f)

    assert f._id == object_id
    assert await Foo.collection.find_one(f._id) is not None


@pytest.mark.asyncio
async def test_update_one(Foo):
    f = Foo()
    await insert_one(f)

    f.x = Inc(100)
    await update_one(f)

    doc = await Foo.collection.find_one(f._id)
    assert doc["x"] == 100


@pytest.mark.asyncio
async def test_update_one_with_fields(Foo):
    f = Foo()
    await insert_one(f)

    f.x = Inc(100)
    f.y = Inc(100)
    await update_one(f, fields=["x"])

    doc = await Foo.collection.find_one(f._id)
    assert doc["x"] == 100
    assert doc["y"] == 0


@pytest.mark.asyncio
async def test_replace_one(Foo):
    f = Foo()
    await insert_one(f)

    f.x = 100
    f.y = 200
    f.z = 300

    await replace_one(f)

    doc = await Foo.collection.find_one(f._id)

    assert doc["x"] == 100
    assert doc["y"] == 200
    assert doc["z"] == 300


@pytest.mark.asyncio
async def test_delete_one(Foo):
    f = Foo()
    await insert_one(f)
    await delete_one(f)

    assert await Foo.collection.find_one(f._id) is None


@pytest.mark.asyncio
async def test_find_one(Foo):
    f = Foo()
    await insert_one(f)

    # Find document that exists
    result = await find_one(Foo, {"_id": f._id})
    assert result._id == f._id

    # find document that does not exist.
    result = await find_one(Foo, {"_id": "abcdef"})
    assert result is None


@pytest.mark.asyncio
async def test_find(Foo):
    f1 = Foo(x=100)
    await insert_one(f1)

    f2 = Foo(x=200)
    await insert_one(f2)

    f3 = Foo(x=300)
    await insert_one(f3)

    cursor = find(Foo, {})
    objects = [foo async for foo in cursor]
    assert len(objects) == 3
    for obj in objects:
        assert isinstance(obj, Foo)


@pytest.mark.asyncio
async def test_not_a_mongoclass():
    @dataclass
    class Foo:
        ...
    
    with pytest.raises(TypeError):
        await insert_one(Foo())
    
    with pytest.raises(TypeError):
        await update_one(Foo())
    
    with pytest.raises(TypeError):
        await replace_one(Foo())
    
    with pytest.raises(TypeError):
        await delete_one(Foo())

    with pytest.raises(TypeError):
        await find_one(Foo, {})

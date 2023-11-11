from dataclasses import dataclass, field
from typing import ClassVar

from bson import ObjectId
import pytest
from mongoclasses import (
    ainsert_one, afind_one, aupdate_one, adelete_one, areplace_one
)


@pytest.fixture
def client():
    from motor.motor_asyncio import AsyncIOMotorClient
    return AsyncIOMotorClient()


@pytest.fixture
def database(client):
    client.drop_database("test_database")
    return client.test_database


@pytest.fixture
def mongoclass(database):
    @dataclass
    class Foo:
        collection: ClassVar = database.test_collection
        _id: ObjectId = field(default_factory=ObjectId)
        name: str = "foo"

    return Foo


@pytest.mark.asyncio
async def test_insert_one(mongoclass):
    obj = mongoclass()
    await ainsert_one(obj)

    assert obj._id is not None
    assert await mongoclass.collection.find_one({"_id": obj._id}) is not None


@pytest.mark.asyncio
async def test_insert_one_not_mongoclass():
    with pytest.raises(TypeError):
        await ainsert_one(object())


@pytest.mark.asyncio
async def test_find_one(mongoclass):
    obj = mongoclass()
    await ainsert_one(obj)

    assert await afind_one(mongoclass, {"_id": obj._id}) == obj


@pytest.mark.asyncio
async def test_find_one_not_mongoclass():
    with pytest.raises(TypeError):
        await afind_one(object(), {"_id": ObjectId()})


@pytest.mark.asyncio
async def test_update_one(mongoclass):
    obj = mongoclass()
    await ainsert_one(obj)
    await aupdate_one(obj, {"$set": {"name": "bar"}})
    result = await afind_one(mongoclass, {"_id": obj._id})
    assert result.name == "bar"


@pytest.mark.asyncio
async def test_update_one_not_mongoclass():
    with pytest.raises(TypeError):
        await aupdate_one(object(), {"$set": {"name": "bar"}})


@pytest.mark.asyncio
async def test_replace_one(mongoclass):
    obj = mongoclass()
    await ainsert_one(obj)
    obj.name = "bar"
    await areplace_one(obj)
    result = await afind_one(mongoclass, {"_id": obj._id})
    assert result.name == "bar"


@pytest.mark.asyncio
async def test_replace_one_not_mongoclass():
    with pytest.raises(TypeError):
        await areplace_one(object())


@pytest.mark.asyncio
async def test_delete_one(mongoclass):
    obj = mongoclass()
    await ainsert_one(obj)
    await adelete_one(obj)
    assert await afind_one(mongoclass, {"_id": obj._id}) is None


@pytest.mark.asyncio
async def test_delete_one_not_mongoclass():
    with pytest.raises(TypeError):
        await adelete_one(object())


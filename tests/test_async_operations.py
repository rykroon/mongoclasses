from dataclasses import dataclass, field
from typing import ClassVar

from bson import ObjectId
import pytest
import pytest_asyncio
from mongoclasses import (
    adelete_one,
    afind_one,
    ainsert_one,
    areplace_one,
    aupdate_one,
    get_id
)


@pytest.fixture
def client():
    from motor.motor_asyncio import AsyncIOMotorClient
    return AsyncIOMotorClient()


@pytest.fixture
def database(client):
    return client.test_database


@pytest_asyncio.fixture(autouse=True)
async def drop_collection(database):
    await database.drop_collection("test_collection")


@pytest.fixture
def Mongoclass(database):
    @dataclass
    class Foo:
        collection: ClassVar = database.test_collection
        _id: ObjectId = field(default_factory=ObjectId)
        name: str = "foo"

    return Foo


@pytest.mark.asyncio
async def test_insert_one(Mongoclass):
    obj = Mongoclass()
    await ainsert_one(obj)

    assert await Mongoclass.collection.count_documents({"_id": obj._id}) == 1


@pytest.mark.asyncio
async def test_insert_one_not_mongoclass():
    with pytest.raises(TypeError):
        await ainsert_one(object())


@pytest.mark.asyncio
async def test_find_one(Mongoclass):
    obj = Mongoclass()
    await ainsert_one(obj)

    result = await afind_one(Mongoclass, {"_id": obj._id})
    assert result._id == obj._id
    assert result.name == "foo"


@pytest.mark.asyncio
async def test_find_one_not_mongoclass():
    with pytest.raises(TypeError):
        await afind_one(object(), {"_id": ObjectId()})


@pytest.mark.asyncio
async def test_update_one(Mongoclass):
    obj = Mongoclass()
    await ainsert_one(obj)
    await aupdate_one(obj, {"$set": {"name": "bar"}})

    result = await afind_one(Mongoclass, {"_id": obj._id})
    assert result.name == "bar"


@pytest.mark.asyncio
async def test_update_one_not_mongoclass():
    with pytest.raises(TypeError):
        await aupdate_one(object(), {"$set": {"name": "bar"}})


@pytest.mark.asyncio
async def test_replace_one(Mongoclass):
    obj = Mongoclass()
    await ainsert_one(obj)
    obj.name = "bar"
    await areplace_one(obj)
    result = await afind_one(Mongoclass, {"_id": obj._id})
    assert result.name == "bar"


@pytest.mark.asyncio
async def test_replace_one_not_mongoclass():
    with pytest.raises(TypeError):
        await areplace_one(object())


@pytest.mark.asyncio
async def test_delete_one(Mongoclass):
    obj = Mongoclass()
    await ainsert_one(obj)
    await adelete_one(obj)
    assert await afind_one(Mongoclass, {"_id": obj._id}) is None


@pytest.mark.asyncio
async def test_delete_one_not_mongoclass():
    with pytest.raises(TypeError):
        await adelete_one(object())


from dataclasses import asdict
from typing import Optional

from bson import ObjectId
import pytest
import pytest_asyncio
from motor.motor_asyncio import AsyncIOMotorClient

from mongoclasses import (
    delete_one, find, find_one, fromdict, insert_one, mongoclass, update_one
)


@pytest_asyncio.fixture
async def database():
    client = AsyncIOMotorClient()
    await client.drop_database('test')
    return client['test']


@pytest.fixture
def Foo(database):
    @mongoclass(db=database)
    class Foo:
        _id: Optional[ObjectId] = None
        name: str = ""
        description: str = ""

    return Foo


@pytest.mark.asyncio
async def test_insert_one_without_id(Foo, database):    
    f = Foo()
    await insert_one(f)

    assert f._id is not None
    assert await database['foo'].find_one({'_id': f._id}) is not None


@pytest.mark.asyncio
async def test_insert_one_with_id(Foo, database):  
    # test scenario where an _id is generated before insertion.  
    object_id = ObjectId()
    f = Foo(_id=object_id)
    await insert_one(f)

    assert f._id == object_id
    assert await database['foo'].find_one({'_id': f._id}) is not None


@pytest.mark.asyncio
async def test_update_one(Foo, database):    
    f = Foo()
    await insert_one(f)

    f.name = "Fred"
    await update_one(f)
    
    doc = await database['foo'].find_one({"_id": f._id})
    assert doc["name"] == "Fred"


@pytest.mark.asyncio
async def test_update_one_with_fields(Foo, database):    
    f = Foo()
    await insert_one(f)

    f.name = "Fred"
    f.description = "foobar"
    await update_one(f, fields=["description"])
    
    doc = await database['foo'].find_one({"_id": f._id})
    assert doc["name"] == ""
    assert doc["description"] == "foobar"
    

@pytest.mark.asyncio
async def test_delete_one(Foo, database):    
    f = Foo()
    await insert_one(f)
    await delete_one(f)

    assert await database['foo'].find_one({"_id": f._id}) is None


@pytest.mark.asyncio
async def test_find_one(Foo):
    f = Foo()
    await insert_one(f)

    # Find document that exists
    result = await find_one(Foo, {'_id': f._id})
    assert result._id == f._id

    # find document that does not exist.
    result = await find_one(Foo, {'_id': "abcdef"})
    assert result is None


@pytest.mark.asyncio
async def test_find(Foo, database):
    f1 = Foo(name="Alice")
    await insert_one(f1)

    f2 = Foo(name="Bob")
    await insert_one(f2)

    f3 = Foo(name="Charlie")
    await insert_one(f3)

    cursor = find(Foo, {})
    objects = [foo async for foo in cursor]
    assert len(objects) == 3


@pytest.mark.asyncio
async def test_fromdict(Foo):
    f1 = Foo()
    f2 = fromdict(Foo, asdict(f1))
    assert f1 == f2


@pytest.mark.asyncio
async def test_non_mongoclasses_in_mongoclass_functions():
    class Foo:
        ...

    with pytest.raises(TypeError):
        f = Foo()
        await insert_one(f)
    
    with pytest.raises(TypeError):
        f = Foo()
        await update_one(f)
    
    with pytest.raises(TypeError):
        f = Foo()
        await delete_one(f)

    with pytest.raises(TypeError):
        await find_one(Foo, {})
    
    with pytest.raises(TypeError):
        find(Foo, {})

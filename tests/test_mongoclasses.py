from bson import ObjectId
import pytest
import pytest_asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from mongoclasses import (
    mongoclass, insert_one, update_one, delete_one, find_one, find, fromdict
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
        _id: ObjectId | None = None
        name: str = ""

    return Foo


def test_mongoclass_creation(database):
    # Missing a database.
    with pytest.raises(AssertionError):
        @mongoclass
        class Foo:
            _id: ObjectId | None = None

    # Missing an _id field.
    with pytest.raises(AssertionError):
        @mongoclass(db=database)
        class Foo:
            ...

    @mongoclass(db=database)
    class Foo:
        _id: ObjectId | None = None
    
    assert Foo.__mongomini_collection__.database == database
    assert Foo.__mongomini_collection__.name == 'foo'


def test_mongoclass_collection_name(database):
    @mongoclass(db=database, collection_name='foobar')
    class Foo:
        _id: ObjectId | None = None
    
    assert Foo.__mongomini_collection__.name == 'foobar'


def test_database_inheritance(database):

    @mongoclass(db=database)
    class Foo:
        _id: ObjectId | None = None

    @mongoclass
    class Bar(Foo):
        ...

    assert Foo.__mongomini_collection__.database == database
    assert Bar.__mongomini_collection__.database == database


@pytest.mark.asyncio
async def test_insert_one(Foo, database):    
    f = Foo()
    await insert_one(f)

    assert f._id is not None
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
    assert result['_id'] == f._id

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
    l = []
    async for foo in cursor:
        l.append(foo)

    assert len(l) == 3


@pytest.mark.asyncio
async def test_fromdict(Foo):
    f1 = Foo()
    await insert_one(f1)

    data = await find_one(Foo, {'_id': f1._id})
    f2 = fromdict(Foo, data)

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

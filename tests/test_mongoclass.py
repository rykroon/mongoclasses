from dataclasses import dataclass
from typing import Optional

from bson import ObjectId
import pytest
import pytest_asyncio
from motor.motor_asyncio import AsyncIOMotorClient

from mongoclasses import mongoclass


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

    return Foo


def test_mongoclass_creation(database):
    # Missing a database.
    with pytest.raises(RuntimeError):
        @mongoclass
        class Foo:
            _id: Optional[ObjectId] = None

    # Missing an _id field.
    with pytest.raises(AttributeError):
        @mongoclass(db=database)
        class Foo:
            ...

    # Valid mongoclass
    @mongoclass(db=database)
    class Foo:
        _id: Optional[ObjectId] = None
    
    assert Foo.__mongoclasses_collection__.database == database
    assert Foo.__mongoclasses_collection__.name == 'foo'

    # Mongoclass being created from an already existing dataclass.
    @dataclass
    class Foo:
        _id: Optional[ObjectId] = None
    
    Foo = mongoclass(db=database)(Foo)
    
    assert Foo.__mongoclasses_collection__.database == database
    assert Foo.__mongoclasses_collection__.name == 'foo'


def test_mongoclass_collection_name(database):
    @mongoclass(db=database, collection_name='foobar')
    class Foo:
        _id: Optional[ObjectId] = None
    
    assert Foo.__mongoclasses_collection__.name == 'foobar'


def test_database_inheritance(database):

    @mongoclass(db=database)
    class Foo:
        _id: Optional[ObjectId] = None

    @mongoclass
    class Bar(Foo):
        ...

    assert Foo.__mongoclasses_collection__.database == database
    assert Bar.__mongoclasses_collection__.database == database

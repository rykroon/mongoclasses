from dataclasses import dataclass, field

from bson import ObjectId
from pymongo import MongoClient
import pytest

from mongoclasses import (
    mongoclass, _get_collection, delete_one, find, find_one, insert_one, update_one
)


@pytest.fixture
def client():
    return MongoClient()


@pytest.fixture(autouse=True)
def drop_database(client):
    client.drop_database("test")


@pytest.fixture
def Foo(client):
    @mongoclass(client["test"])
    class Foo:
        _id: ObjectId = field(default_factory=ObjectId)
        name: str = ""
        description: str = ""

    return Foo


class TestInsertOne:

    def test_insert_one(self, Foo):
        # test scenario where an _id is generated before insertion.
        f = Foo()
        insert_one(f)

        assert _get_collection(Foo).find_one(f._id) is not None

    def test_type_error(self):
        @dataclass
        class Foo:
            ...
        
        with pytest.raises(TypeError):
            insert_one(Foo())


class TestUpdateOne:
    def test_success(self, Foo):
        f = Foo()
        insert_one(f)

        f.name = "Fred"
        update_one(f)

        doc = _get_collection(Foo).find_one(f._id)
        assert doc["name"] == "Fred"

    def test_fields(self, Foo):
        f = Foo()
        insert_one(f)

        f.name = "Fred"
        f.description = "Hello World"
        update_one(f, fields=["name"])

        doc = _get_collection(Foo).find_one(f._id)
        assert doc["name"] == "Fred"
        assert doc["description"] == ""
    
    def test_type_error(self):
        @dataclass
        class Foo:
            ...
        
        with pytest.raises(TypeError):
            update_one(Foo())


class TestDeleteOne:
    def test_success(self, Foo):
        f = Foo()
        insert_one(f)
        delete_one(f)

        assert _get_collection(Foo).find_one(f._id) is None
    
    def test_type_error(self):
        @dataclass
        class Foo:
            ...
        
        with pytest.raises(TypeError):
            delete_one(Foo())


class TestFindOne:

    def test_success(self, Foo):
        f = Foo()
        insert_one(f)

        # Find document that exists
        result = find_one(Foo, {"_id": f._id})
        assert result._id == f._id

        # find document that does not exist.
        result = find_one(Foo, {"_id": "abcdef"})
        assert result is None
    
    def test_type_error(self):
        @dataclass
        class Foo:
            ...

        with pytest.raises(TypeError):
            find_one(Foo)


class TestFind:
    def test_find(self, Foo):
        f1 = Foo(name="Alice")
        insert_one(f1)

        f2 = Foo(name="Bob")
        insert_one(f2)

        f3 = Foo(name="Charlie")
        insert_one(f3)

        cursor = find(Foo, {})
        objects = [foo for foo in cursor]
        assert len(objects) == 3
        for obj in objects:
            assert isinstance(obj, Foo)

    def test_type_error(self):
        @dataclass
        class Foo:
            ...
        
        with pytest.raises(TypeError):
            find(Foo, {})

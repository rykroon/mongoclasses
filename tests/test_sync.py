from dataclasses import dataclass
from typing import ClassVar, Optional

from bson import ObjectId
from pymongo import MongoClient
from pymongo.collection import Collection
import pytest

from mongoclasses import delete_one, find, find_one, insert_one, update_one


@pytest.fixture
def client():
    return MongoClient()


@pytest.fixture(autouse=True)
def drop_database(client):
    client.drop_database("test")


@pytest.fixture
def test_collection(client):
    db = client["test"]
    return db["test_collection"]


@pytest.fixture
def Foo(test_collection):
    @dataclass
    class Foo:
        collection: ClassVar[Collection] = test_collection
        _id: Optional[ObjectId] = None
        name: str = ""
        description: str = ""

    return Foo


class TestInsertOne:
    def test_insert_one_without_id(self, Foo):
        f = Foo()
        insert_one(f)

        assert f._id is not None
        assert Foo.collection.find_one({"_id": f._id}) is not None

    def test_insert_one_with_id(self, Foo):
        # test scenario where an _id is generated before insertion.
        object_id = ObjectId()
        f = Foo(_id=object_id)
        insert_one(f)

        assert f._id == object_id
        assert Foo.collection.find_one({"_id": f._id}) is not None
    
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

        doc = Foo.collection.find_one({"_id": f._id})
        assert doc["name"] == "Fred"

    def test_fields(self, Foo):
        f = Foo()
        insert_one(f)

        f.name = "Fred"
        f.description = "Hello World"
        update_one(f, fields=["name"])

        doc = Foo.collection.find_one({"_id": f._id})
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

        assert Foo.collection.find_one({"_id": f._id}) is None
    
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

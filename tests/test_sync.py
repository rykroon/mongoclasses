from dataclasses import dataclass, field
from typing import ClassVar

from bson import ObjectId
from pymongo import MongoClient
from pymongo.collection import Collection
import pytest

from mongoclasses import delete_one, find, find_one, insert_one, replace_one, update_one
from mongoclasses.operators import update as upd

@pytest.fixture
def client():
    return MongoClient()


@pytest.fixture(autouse=True)
def drop_database(client):
    client.drop_database("test")


@pytest.fixture
def Foo(client):
    @dataclass
    class Foo:
        collection: ClassVar[Collection] = client["test"]["foo"]
        _id: ObjectId = field(default_factory=ObjectId)
        x: int = 0
        y: int = 0
        z: int = 0

    return Foo


class TestInsertOne:

    def test_insert_one(self, Foo):
        # test scenario where an _id is generated before insertion.
        f = Foo()
        insert_one(f)

        assert Foo.collection.find_one(f._id) is not None

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

        update_one(f, upd.set(x=100))

        doc = Foo.collection.find_one(f._id)
        assert doc["x"] == 100
    
    def test_type_error(self):
        @dataclass
        class Foo:
            ...
        
        with pytest.raises(TypeError):
            update_one(Foo())


class TestReplaceOne:

    def test_replace_one(self, Foo):
        f = Foo()
        insert_one(f)

        f.x = 100
        f.y = 200
        f.z = 300

        replace_one(f)

        doc = Foo.collection.find_one(f._id)

        assert doc["x"] == 100
        assert doc["y"] == 200
        assert doc["z"] == 300

    def test_upsert(self, Foo):
        f = Foo()
        replace_one(f)
        assert Foo.collection.find_one(f._id) is None

        replace_one(f, upsert=True)
        assert Foo.collection.find_one(f._id) is not None

    def test_type_error(self):
        @dataclass
        class Foo:
            ...
        
        with pytest.raises(TypeError):
            replace_one(Foo())


class TestDeleteOne:
    def test_success(self, Foo):
        f = Foo()
        insert_one(f)
        delete_one(f)

        assert Foo.collection.find_one(f._id) is None
    
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
        f1 = Foo(x=100)
        insert_one(f1)

        f2 = Foo(x=200)
        insert_one(f2)

        f3 = Foo(x=300)
        insert_one(f3)

        cursor = find(Foo, {})
        objects = [foo for foo in cursor]
        assert len(objects) == 3
        for obj in objects:
            assert isinstance(obj, Foo)
    
    def test_sort_ascending(self, Foo):
        f2 = Foo(x=300)
        insert_one(f2)

        f1 = Foo(x=100)
        insert_one(f1)

        f3 = Foo(x=200)
        insert_one(f3)

        cursor = find(Foo, {}, sort=["x"])
        objects = [foo for foo in cursor]
        assert objects[0].x == 100
        assert objects[1].x == 200
        assert objects[2].x == 300

    def test_sort_descending(self, Foo):
        f2 = Foo(x=300)
        insert_one(f2)

        f1 = Foo(x=100)
        insert_one(f1)

        f3 = Foo(x=200)
        insert_one(f3)

        cursor = find(Foo, {}, sort=["-x"])
        objects = [foo for foo in cursor]
        assert objects[0].x == 300
        assert objects[1].x == 200
        assert objects[2].x == 100

    def test_type_error(self):
        @dataclass
        class Foo:
            ...
        
        with pytest.raises(TypeError):
            find(Foo, {})

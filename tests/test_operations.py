from dataclasses import dataclass, field
from typing import ClassVar

from bson import ObjectId
import pytest
from mongoclasses import (
    insert_one,
    iter_objects,
    find_one,
    find,
    update_one,
    delete_one,
    replace_one,
)


@pytest.fixture
def client():
    from pymongo import MongoClient
    return MongoClient()

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


def test_insert_one(mongoclass):
    obj = mongoclass()
    insert_one(obj)

    assert obj._id is not None
    assert mongoclass.collection.find_one({"_id": obj._id}) is not None


def test_insert_one_not_mongoclass():
    with pytest.raises(TypeError):
        insert_one(object())


def test_find_one(mongoclass):
    obj = mongoclass()
    insert_one(obj)

    assert find_one(mongoclass, {"_id": obj._id}) == obj


def test_find_one_not_mongoclass():
    with pytest.raises(TypeError):
        find_one(object(), {"_id": ObjectId()})


def test_update_one(mongoclass):
    obj = mongoclass()
    insert_one(obj)
    update_one(obj, {"$set": {"name": "bar"}})
    assert find_one(mongoclass, {"_id": obj._id}).name == "bar"


def test_update_one_not_mongoclass():
    with pytest.raises(TypeError):
        update_one(object(), {"$set": {"name": "bar"}})


def test_replace_one(mongoclass):
    obj = mongoclass()
    insert_one(obj)
    obj.name = "bar"
    replace_one(obj)
    assert find_one(mongoclass, {"_id": obj._id}).name == "bar"


def test_replace_one_not_mongoclass():
    with pytest.raises(TypeError):
        replace_one(object())


def test_delete_one(mongoclass):
    obj = mongoclass()
    insert_one(obj)
    delete_one(obj)
    assert find_one(mongoclass, {"_id": obj._id}) is None


def test_delete_one_not_mongoclass():
    with pytest.raises(TypeError):
        delete_one(object())


def test_find(mongoclass):
    obj = mongoclass()
    insert_one(obj)
    cursor = find(mongoclass, {"_id": obj._id})
    document = next(cursor)
    assert document["_id"] == obj._id


def test_find_not_mongoclass():
    with pytest.raises(TypeError):
        find(object(), {"_id": ObjectId()})


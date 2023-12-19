from dataclasses import dataclass, field

from bson import ObjectId
import pytest
from mongoclasses import (
    mongoclass,
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
def Mongoclass(database):
    @mongoclass(db=database, collection_name="test_collection")
    @dataclass
    class Foo:
        _id: ObjectId = field(default_factory=ObjectId)
        name: str = "foo"

    return Foo


def test_insert_one(Mongoclass):
    obj = Mongoclass()
    insert_one(obj)

    assert obj._id is not None
    collection = Mongoclass.__mongoclass_config__.collection
    assert collection.find_one({"_id": obj._id}) is not None


def test_insert_one_not_mongoclass():
    with pytest.raises(TypeError):
        insert_one(object())


def test_find_one(Mongoclass):
    obj = Mongoclass()
    insert_one(obj)

    assert find_one(Mongoclass, {"_id": obj._id}) == obj


def test_find_one_not_mongoclass():
    with pytest.raises(TypeError):
        find_one(object(), {"_id": ObjectId()})


def test_update_one(Mongoclass):
    obj = Mongoclass()
    insert_one(obj)
    update_one(obj, {"$set": {"name": "bar"}})
    assert find_one(Mongoclass, {"_id": obj._id}).name == "bar"


def test_update_one_not_mongoclass():
    with pytest.raises(TypeError):
        update_one(object(), {"$set": {"name": "bar"}})


def test_replace_one(Mongoclass):
    obj = Mongoclass()
    insert_one(obj)
    obj.name = "bar"
    replace_one(obj)
    assert find_one(Mongoclass, {"_id": obj._id}).name == "bar"


def test_replace_one_not_mongoclass():
    with pytest.raises(TypeError):
        replace_one(object())


def test_delete_one(Mongoclass):
    obj = Mongoclass()
    insert_one(obj)
    delete_one(obj)
    assert find_one(Mongoclass, {"_id": obj._id}) is None


def test_delete_one_not_mongoclass():
    with pytest.raises(TypeError):
        delete_one(object())


def test_find(Mongoclass):
    obj = Mongoclass()
    insert_one(obj)
    cursor = find(Mongoclass, {"_id": obj._id})
    document = next(cursor)
    assert document["_id"] == obj._id


def test_find_not_mongoclass():
    with pytest.raises(TypeError):
        find(object(), {"_id": ObjectId()})


def test_iter_objects(Mongoclass):
    obj1 = Mongoclass()
    obj2 = Mongoclass()
    insert_one(obj1)
    insert_one(obj2)
    cursor = find(Mongoclass, {})
    for obj in iter_objects(Mongoclass, cursor):
        assert isinstance(obj, Mongoclass)
        assert obj._id in [obj1._id, obj2._id]

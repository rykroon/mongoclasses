import dataclasses as dc
from typing import Any

from bson import ObjectId, SON
import cattrs
from pymongo import MongoClient
from typing_extensions import Annotated

import pytest

from mongoclasses import (
    _get_field_meta,
    _get_field_name,
    mongoclass,
    is_mongoclass,
    get_id,
    set_id,
    get_collection,
    get_converter,
    to_document,
    from_document,
    DeveloperError,
    FieldMeta,
)


@pytest.fixture
def client():
    return MongoClient()


@pytest.fixture
def database(client):
    client.drop_database("test_database")
    return client.test_database


def test_is_mongoclass(database):
    assert not is_mongoclass(object)
    assert not is_mongoclass(object())

    @dc.dataclass
    class Foo:
        pass

    assert not is_mongoclass(Foo)
    assert not is_mongoclass(Foo())

    @mongoclass(db=database)
    class Bar:
        _id: Any = ""

    assert is_mongoclass(Bar)
    assert is_mongoclass(Bar())


def test_mongoclass(database):
    @mongoclass(db=database)
    class Foo:
        _id: ObjectId = dc.field(default_factory=ObjectId)

    assert is_mongoclass(Foo)


def test_mongoclass_missing_db():
    with pytest.raises(DeveloperError):
        @mongoclass()
        class Foo:
            pass


def test_mongoclass_inherit_database(database):
    @mongoclass(db=database)
    class Foo:
        _id: ObjectId = dc.field(default_factory=ObjectId)

    @mongoclass
    class Bar(Foo):
        pass

    assert Bar.__mongoclass_config__.collection.name == "foo.bar"


def test_mongoclass_missing_id_field(database):
    with pytest.raises(DeveloperError):
        @mongoclass(db=database)
        class Foo:
            pass

    with pytest.raises(DeveloperError):
        @mongoclass(db=database)
        class Foo:
            _id: Annotated[int, FieldMeta(db_field="not_id")] = 0


def test_mongoclass_with_unique_field(database):
    @mongoclass(db=database)
    class Foo:
        _id: ObjectId = dc.field(default_factory=ObjectId)
        name: Annotated[str, FieldMeta(unique=True)] = ""

    assert [idx.document for idx in Foo.__mongoclass_config__.indexes] == [
        {"name": "name_1", "unique": True, "key": SON([("name", 1)])}
    ]


def test_get_field_meta(database):
    @mongoclass(db=database)
    class Foo:
        annotated_with_fieldmeta: Annotated[int, FieldMeta(db_field="_id")] = 0
        annotated_without_fieldmeta: Annotated[int, ""] = 0
        not_annotated: int = 0

    fields = dc.fields(Foo)
    assert _get_field_meta(fields[0]) == FieldMeta(db_field="_id")
    assert _get_field_meta(fields[1]) is None
    assert _get_field_meta(fields[2]) is None


def test_get_field_name(database):
    @mongoclass(db=database)
    class Foo:
        id: Annotated[int, FieldMeta(db_field="_id")] = 0
        name: str = ""
        description: Annotated[str, FieldMeta()] = ""

    fields = dc.fields(Foo)
    assert _get_field_name(fields[0]) == "_id"
    assert _get_field_name(fields[1]) == "name"
    assert _get_field_name(fields[2]) == "description"


def test_get_id_and_set_id(database):
    @mongoclass(db=database)
    class Foo:
        _id: ObjectId = dc.field(default_factory=ObjectId)

    f = Foo()
    assert get_id(f) == f._id
    new_id = ObjectId()
    set_id(f, new_id)
    assert get_id(f) == f._id == new_id

    # test with field override.
    @mongoclass(db=database)
    class Foo:
        id: Annotated[ObjectId, FieldMeta(db_field="_id")] = dc.field(default_factory=ObjectId)

    f = Foo()
    assert get_id(f) == f.id
    new_id = ObjectId()
    set_id(f, new_id)
    assert get_id(f) == f.id == new_id

    # test not a mongoclass.
    with pytest.raises(TypeError):
        get_id(object())
    
    with pytest.raises(TypeError):
        set_id(object(), 1)


def test_get_collection(database):
    @mongoclass(db=database)
    class Foo:
        _id: ObjectId = dc.field(default_factory=ObjectId)

    collection = get_collection(Foo)
    assert collection.database == database
    assert collection.name == "foo"


def test_get_collection_with_custom_name(database):
    @mongoclass(db=database, collection_name="foobar")
    class Foo:
        _id: ObjectId = dc.field(default_factory=ObjectId)

    collection = get_collection(Foo)
    assert collection.database == database
    assert collection.name == "foobar"


def test_get_collection_not_a_mongoclass():
    with pytest.raises(TypeError):
        get_collection(object())


def test_get_converter(database):
    @mongoclass(db=database)
    class Foo:
        _id: ObjectId = dc.field(default_factory=ObjectId)
        name: str = ""
        description: Annotated[str, FieldMeta()] = ""

    converter = get_converter(Foo)
    assert isinstance(converter, cattrs.Converter)

    with pytest.raises(TypeError):
        get_converter(object())


def test_to_document_with_field_overrides(database):
    @mongoclass(db=database)
    class Foo:
        id: Annotated[int, FieldMeta(db_field="_id")] = 0

    f = Foo()
    data = to_document(f)
    assert "_id" in data
    assert "id" not in data


def test_from_document(database):
    @mongoclass(db=database)
    class Foo:
        _id: ObjectId = dc.field(default_factory=ObjectId)
        name: str = ""
        description: Annotated[str, FieldMeta()] = ""

    f = Foo()
    data = to_document(f)
    f2 = from_document(Foo, data)
    assert f2._id == f._id
    assert f2.name == f.name
    assert f2.description == f.description
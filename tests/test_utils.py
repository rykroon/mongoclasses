from dataclasses import dataclass, fields
from typing import ClassVar
from typing_extensions import Annotated  # Introduced in Python 3.9

import pytest

from mongoclasses import (
    get_id,
    get_field_meta,
    get_field_name,
    set_id,
    FieldMeta,
    is_mongoclass,
    mongoclass,
)


def test_get_field_meta():
    @dataclass
    class Foo:
        bar: str  # no annotation
        baz: Annotated[int, FieldMeta(db_field="baz")]  # annotated with FieldMeta
        qux: Annotated[int, ...]  # annotated without FieldMeta

    assert get_field_meta(fields(Foo)[0]) is None
    assert get_field_meta(fields(Foo)[1]) == FieldMeta(db_field="baz")
    assert get_field_meta(fields(Foo)[2]) is None


def test_get_field_name():
    @dataclass
    class Foo:
        bar: str  # no annotation
        baz: Annotated[int, FieldMeta(db_field="bazzz")]  # annotated with FieldMeta
        qux: Annotated[int, ...]  # annotated without FieldMeta

    assert get_field_name(fields(Foo)[0]) == "bar"
    assert get_field_name(fields(Foo)[1]) == "bazzz"
    assert get_field_name(fields(Foo)[2]) == "qux"


def test_get_id():
    @mongoclass(db={"foo": None}, collection_name="foo")
    @dataclass
    class Foo:
        bar: Annotated[int, FieldMeta(db_field="_id")]
        baz: str

    foo = Foo(1, "baz")
    assert get_id(foo) == 1


def test_set_id():
    @mongoclass(db={"foo": None}, collection_name="foo")
    @dataclass
    class Foo:
        bar: Annotated[int, FieldMeta(db_field="_id")]
        baz: str

    foo = Foo(1, "baz")
    set_id(foo, 2)
    assert get_id(foo) == 2


def test_is_mongoclass_not_a_dataclass():
    class NotDataclass:
        pass

    assert not is_mongoclass(NotDataclass)
    assert not is_mongoclass(NotDataclass())


def test_is_mongoclass_no_collection():
    @dataclass
    class Mongoclass:
        pass

    assert not is_mongoclass(Mongoclass)
    assert not is_mongoclass(Mongoclass())


def test_is_mongoclass_collection_not_classvar():
    @dataclass
    class Mongoclass:
        collection: str = ""

    assert not is_mongoclass(Mongoclass)
    assert not is_mongoclass(Mongoclass())


def test_is_mongoclass_no_id():

    with pytest.raises(TypeError):

        @mongoclass(db={"foo": None}, collection_name="foo")
        @dataclass
        class Mongoclass:
            pass


def test_is_mongoclass():
    @mongoclass(db={"foo": None}, collection_name="foo")
    @dataclass
    class Mongoclass:
        _id: str = ""

    assert is_mongoclass(Mongoclass)
    assert is_mongoclass(Mongoclass())

    # assert is_mongoclass_type(Mongoclass)
    # assert not is_mongoclass_type(Mongoclass())

    # assert not is_mongoclass_instance(Mongoclass)
    # assert is_mongoclass_instance(Mongoclass())


def test_is_mongoclass_annotated_id():
    @mongoclass(db={"foo": None}, collection_name="foo")
    @dataclass
    class Mongoclass:
        id: Annotated[str, FieldMeta(db_field="_id")] = ""

    assert is_mongoclass(Mongoclass)
    assert is_mongoclass(Mongoclass())

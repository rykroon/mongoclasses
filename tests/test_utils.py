from dataclasses import dataclass, fields
from typing import List, Optional
from typing_extensions import Annotated # Introduced in Python 3.9

import pytest

from mongoclasses.utils import (
    get_id,
    get_id_field,
    get_field_info,
    get_field_name,
    set_id,
    resolve_type,
    FieldInfo
)


def test_get_field_info():
    @dataclass
    class Foo:
        bar: str # no annotation
        baz: Annotated[int, FieldInfo(db_field="baz")] # annotated with FieldInfo
        qux: Annotated[int, ...] # annotated without FieldInfo


    assert get_field_info(fields(Foo)[0]) is None
    assert get_field_info(fields(Foo)[1]) == FieldInfo(db_field="baz")
    assert get_field_info(fields(Foo)[2]) is None


def test_get_field_name():
    @dataclass
    class Foo:
        bar: str # no annotation
        baz: Annotated[int, FieldInfo(db_field="bazzz")] # annotated with FieldInfo
        qux: Annotated[int, ...] # annotated without FieldInfo


    assert get_field_name(fields(Foo)[0]) == "bar"
    assert get_field_name(fields(Foo)[1]) == "bazzz"
    assert get_field_name(fields(Foo)[2]) == "qux"


def test_get_id_field():
    @dataclass
    class Foo:
        bar: Annotated[int, FieldInfo(db_field="_id")]
        baz: str


    assert get_id_field(Foo) == fields(Foo)[0]


def test_get_id_field_no_id():
    @dataclass
    class Foo:
        bar: str
        baz: str


    with pytest.raises(TypeError):
        get_id_field(Foo)


def test_get_id():
    @dataclass
    class Foo:
        bar: Annotated[int, FieldInfo(db_field="_id")]
        baz: str


    foo = Foo(1, "baz")
    assert get_id(foo) == 1


def test_set_id():
    @dataclass
    class Foo:
        bar: Annotated[int, FieldInfo(db_field="_id")]
        baz: str


    foo = Foo(1, "baz")
    set_id(foo, 2)
    assert get_id(foo) == 2


def test_resolve_type():
    assert resolve_type(int) == int
    assert resolve_type(Annotated[int, ...]) == int # test for Annotated types
    assert resolve_type(Optional[int]) == (int, type(None)) # test for Union types
    assert resolve_type(List[str]) == list

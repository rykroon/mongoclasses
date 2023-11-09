from dataclasses import dataclass, fields
from typing import Annotated, Optional


from mongoclasses.utils import (
    get_field_info, get_field_name, resolve_type, FieldInfo
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


def test_resolve_type():
    assert resolve_type(int) == int
    assert resolve_type(Annotated[int, ...]) == int # test for Annotated types
    assert resolve_type(Optional[int]) == (int, type(None)) # test for Union types
    assert resolve_type(list[str]) == list

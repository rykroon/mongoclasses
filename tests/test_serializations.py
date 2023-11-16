from dataclasses import dataclass, field
import pytest
from typing import List, Dict
from mongoclasses.serialization import to_document, from_document


def test_to_document():
    @dataclass
    class Inner:
        value: int

    @dataclass
    class Outer:
        foo: Inner
        bar: List[Inner]
        baz: Dict[str, Inner]

    obj = Outer(
        foo=Inner(1),
        bar=[Inner(2), Inner(3)],
        baz={"k1": Inner(4), "k2": Inner(5)},
    )
    assert to_document(obj) == {
        "foo": {"value": 1},
        "bar": [{"value": 2}, {"value": 3}],
        "baz": {"k1": {"value": 4}, "k2": {"value": 5}},
    }


def test_to_document_not_a_dataclass_instance():
    with pytest.raises(TypeError):
        to_document("foo")


def test_from_document_not_a_class():
    with pytest.raises(TypeError):
        from_document("foo", {})


def test_from_document_not_a_dataclass():
    class Foo:
        pass

    with pytest.raises(TypeError):
        from_document(Foo, {})


def test_from_document_dataclass():
    @dataclass
    class Foo:
        bar: str
        baz: int

    assert from_document(Foo, {"bar": "bar", "baz": 1}) == Foo("bar", 1)


def test_from_document_missing_field():
    @dataclass
    class Foo:
        bar: str
        baz: int = 0

    assert from_document(Foo, {"bar": "bar"}) == Foo("bar", 0)


def test_from_document_nested_dataclass():
    @dataclass
    class Foo:
        bar: str
        baz: int

    @dataclass
    class Bar:
        foo: Foo

    assert from_document(Bar, {"foo": {"bar": "bar", "baz": 1}}) == Bar(Foo("bar", 1))


def test_from_document_non_init_field():
    @dataclass
    class Foo:
        bar: str
        baz: int = field(init=False, default=0)

    foo = Foo("bar")
    foo.baz = 1
    assert from_document(Foo, {"bar": "bar", "baz": 1}) == foo

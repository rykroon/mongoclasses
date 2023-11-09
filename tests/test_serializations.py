from dataclasses import dataclass, field
import pytest
from mongoclasses import to_document, from_document


def test_to_document_dataclass():
    @dataclass
    class Foo:
        bar: str
        baz: int

    foo = Foo("bar", 1)
    assert to_document(foo) == {"bar": "bar", "baz": 1}


def test_to_document_nested_dataclass():
    @dataclass
    class Foo:
        bar: str
        baz: int

    @dataclass
    class Bar:
        foo: Foo

    bar = Bar(Foo("bar", 1))
    assert to_document(bar) == {"foo": {"bar": "bar", "baz": 1}}


def test_to_document_list_of_dataclasses():
    @dataclass
    class Foo:
        bar: str
        baz: int

    foo = Foo("bar", 1)
    assert to_document([foo, foo]) == [
        {"bar": "bar", "baz": 1},
        {"bar": "bar", "baz": 1},
    ]


def test_to_document_dict_of_dataclasses():
    @dataclass
    class Foo:
        bar: str
        baz: int

    foo = Foo("bar", 1)
    assert to_document({"foo": foo}) == {"foo": {"bar": "bar", "baz": 1}}


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

    assert from_document(Bar, {"foo": {"bar": "bar", "baz": 1}}) == Bar(
        Foo("bar", 1)
    )


def test_from_document_non_init_field():
    @dataclass
    class Foo:
        bar: str
        baz: int = field(init=False, default=0)

    foo = Foo("bar")
    foo.baz = 1
    assert from_document(Foo, {"bar": "bar", "baz": 1}) == foo

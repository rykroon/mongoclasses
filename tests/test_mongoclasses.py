from dataclasses import dataclass, field, MISSING
from typing import ClassVar

from pymongo.collection import Collection
import pytest

from mongoclasses import is_mongoclass, from_document, to_document


class TestIsMongoclass:

    """
    Tests for the is_mongoclass()
    """

    def test_not_a_dataclass(self):
        class Foo:
            ...
        
        assert is_mongoclass(Foo) is False
        assert is_mongoclass(Foo()) is False

    def test_missing_collection(self):
        @dataclass
        class Foo:
            ...

        assert is_mongoclass(Foo) is False
        assert is_mongoclass(Foo()) is False
    
    def test_collection_not_classvar(self):
        @dataclass
        class Foo:
            collection: str = ""

        assert is_mongoclass(Foo) is False
        assert is_mongoclass(Foo()) is False

    def test_missing_id(self):
        @dataclass
        class Foo:
            collection: ClassVar[Collection]
        
        assert is_mongoclass(Foo) is False
        assert is_mongoclass(Foo()) is False

    def test_explicit_id_field(self):
        @dataclass
        class MyClass:
            collection: ClassVar[Collection]
            _id: int = 0

        assert is_mongoclass(MyClass) is True
        assert is_mongoclass(MyClass()) is True
    
    def test_id_field_override(self):
        @dataclass
        class MyClass:
            collection: ClassVar[Collection]
            id: int = field(default=0, metadata={"mongoclasses": {"db_field": "_id"}})

        assert is_mongoclass(MyClass) is True
        assert is_mongoclass(MyClass()) is True


class TestToDocument:

    def test_nested_dataclass(self):
        @dataclass
        class Inner:
            a: int
        
        @dataclass
        class Outer:
            i: Inner

        obj = Outer(i=Inner(a=1))
        assert to_document(obj) == {"i": {"a": 1}}


class TestFromDocument:

    def test_nested_dataclass(self):
        @dataclass
        class Inner:
            a: int
        
        @dataclass
        class Outer:
            i: Inner

        data = {"i": {"a": 1}}
        assert from_document(Outer, data) == Outer(i=Inner(a=1))
    
    def test_extra_data(self):
        @dataclass
        class MyClass:
            a: int
        
        assert from_document(MyClass, {"a": 1, "b": 2}) == MyClass(a=1)

    def test_defaults(self):
        @dataclass
        class MyClass:
            a: int
            b: int = 2
            c: int = field(default_factory=lambda: 3)

        obj = from_document(MyClass, {})
        assert obj.a == MISSING
        assert obj.b == 2
        assert obj.c == 3
    
    def test_non_init_fields(self):
        @dataclass
        class MyClass:
            a: int
            b: int = field(init=False)
        
        obj  = MyClass(a=1)
        obj.b = 2
        assert from_document(MyClass, {"a": 1, "b": 2}) == obj
    
    def test_type_error(self):
        # not a dataclass.
        class MyClass:
            ...

        with pytest.raises(TypeError):
            from_document(MyClass, {})
        
        with pytest.raises(TypeError):
            from_document(None, {})
    
from dataclasses import dataclass, is_dataclass, field
from typing import ClassVar

from pymongo import MongoClient
import pytest

from mongoclasses import is_mongoclass, from_document, to_document


@pytest.fixture
def client():
    return MongoClient()


class TestIsMongoclass:

    """
    Tests for the is_mongoclass()
    """

    def test_just_a_class(self):
        class MyClass:
            ...

        assert is_mongoclass(MyClass) is False
    
    def test_just_a_dataclass(self):
        @dataclass
        class MyClass:
            ...
        
        assert is_mongoclass(MyClass) is False
    
    def test_is_a_mongoclass(self, client):
        @dataclass
        class MyClass:
            collection: ClassVar[...] = client["test"]["myclass"]
            _id: int = 0

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
    
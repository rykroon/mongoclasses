from dataclasses import dataclass, field, MISSING
from typing import Any

import pytest
from mongoclasses import from_document, to_document


@pytest.fixture
def Foo():
    @dataclass
    class Foo:
        x: Any
    return Foo

class TestToDocument:

    def test_nested_dataclass(self, Foo):

        obj = Foo(x=Foo(x=1))
        assert to_document(obj) == {"x": {"x": 1}}

    def test_list(self, Foo):
        obj = Foo(x=[1, 2, 3])
        assert to_document(obj) == {"x": [1, 2, 3]}

    def test_dict(self, Foo):
        obj = Foo(x={"a": 1})
        assert to_document(obj) == {"x": {"a": 1}}


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

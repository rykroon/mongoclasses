from dataclasses import InitVar, dataclass, field
from typing import Any, ClassVar

from motor.motor_asyncio import AsyncIOMotorCollection
from mongoclasses import asdict, is_mongoclass, _is_mongoclass_instance
import pytest


class TestIsMongoclass:

    """
    Tests for the is_mongoclass(), _is_mongoclass_instance(),
    and _is_mongoclass_type() functions.
    """

    def test_not_a_dataclass(self):
        class MyClass:
            ...

        assert is_mongoclass(MyClass) is False
        assert is_mongoclass(MyClass()) is False

        assert _is_mongoclass_instance(MyClass) is False
        assert _is_mongoclass_instance(MyClass()) is False

    def test_no_id_and_no_collection(self):
        @dataclass
        class MyClass:
            ...

        assert is_mongoclass(MyClass) is False
        assert is_mongoclass(MyClass()) is False

        assert _is_mongoclass_instance(MyClass) is False
        assert _is_mongoclass_instance(MyClass()) is False

    def test_no_collection(self):
        @dataclass
        class MyClass:
            _id: Any = None
        
        assert is_mongoclass(MyClass) is False
        assert is_mongoclass(MyClass()) is False

        assert _is_mongoclass_instance(MyClass) is False
        assert _is_mongoclass_instance(MyClass()) is False

    def test_no_id(self):
        @dataclass
        class MyClass:
            collection: ClassVar[AsyncIOMotorCollection]
        
        assert is_mongoclass(MyClass) is False
        assert is_mongoclass(MyClass()) is False

        assert _is_mongoclass_instance(MyClass) is False
        assert _is_mongoclass_instance(MyClass()) is False

    def test_incorrect_field_type_for_id(self):
        @dataclass
        class MyClass:
            collection: ClassVar[AsyncIOMotorCollection] = None
            _id: InitVar[Any] = None
        
        assert is_mongoclass(MyClass) is False
        assert is_mongoclass(MyClass()) is False

        assert _is_mongoclass_instance(MyClass) is False
        assert _is_mongoclass_instance(MyClass()) is False

    def test_incorrect_field_type_for_collection(self):
        @dataclass
        class MyClass:
            collection: AsyncIOMotorCollection = None
            _id: Any = None
        
        assert is_mongoclass(MyClass) is False
        assert is_mongoclass(MyClass()) is False

        assert _is_mongoclass_instance(MyClass) is False
        assert _is_mongoclass_instance(MyClass()) is False

    def test_success(self):
        @dataclass
        class MyClass:
            collection: ClassVar[AsyncIOMotorCollection] = None
            _id: Any = None
        
        assert is_mongoclass(MyClass) is True
        assert is_mongoclass(MyClass()) is True

        assert _is_mongoclass_instance(MyClass) is False
        assert _is_mongoclass_instance(MyClass()) is True


class TestAsDict:

    def test_not_a_dataclass(self):
        class MyClass:
            ...
        
        obj = MyClass()

        with pytest.raises(TypeError):
            asdict(obj)
    
    def test_cannot_specify_include_and_exclude(self):
        @dataclass
        class Foo:
            a: int = 0
        
        f = Foo()

        with pytest.raises(ValueError):
            asdict(f, include=["a"], exclude=["a"])

    def test_recursive_dataclass(self):
        @dataclass
        class Inner:
            a: int = 0
        
        @dataclass
        class Outer:
            i: Inner = field(default_factory=Inner)
        
        data = asdict(Outer())

        assert isinstance(data, dict)
        assert isinstance(data["i"], dict)

    def test_dataclass_in_list(self):
        @dataclass
        class Inner:
            a: int = 0
        
        @dataclass
        class Outer:
            inner_list: list = field(default_factory=list)
        
        obj = Outer()
        obj.inner_list.append(Inner())

        data = asdict(obj)

        assert isinstance(data, dict)
        assert isinstance(data["inner_list"], list)
        assert isinstance(data["inner_list"][0], dict)

    def test_dataclass_in_dict(self):
        @dataclass
        class Inner:
            s: int = 0
        
        @dataclass
        class Outer:
            inner_dict: dict = field(default_factory=dict)
        
        obj = Outer()
        obj.inner_dict["one"] = Inner()

        data = asdict(obj)

        assert isinstance(data, dict)
        assert isinstance(data["inner_dict"], dict)
        assert isinstance(data["inner_dict"]["one"], dict)

    def test_list_and_tuples(self):
        @dataclass
        class Foo:
            lst: list
            tpl: tuple
        
        foo = Foo(lst=[1, 2, 3], tpl=(1, 2, 3))

        data = asdict(foo)
        assert isinstance(data, dict)
        assert isinstance(data["lst"], list)
        assert isinstance(data["tpl"], list)

    def test_sets_and_frozensets(self):
        @dataclass
        class Foo:
            set: set
            fset: frozenset

        foo = Foo(set={1, 2, 3}, fset=frozenset({1, 2, 3}))

        data = asdict(foo)
        assert isinstance(data, dict)
        assert isinstance(data["set"], list)
        assert isinstance(data["fset"], list)
    
    def test_include(self):
        @dataclass
        class Foo:
            a: int = 0
            b: int = 0
        
        foo = Foo()

        data = asdict(foo, include=["a"])
        assert list(data.keys()) == ["a"]

    def test_exclude(self):
        @dataclass
        class Foo:
            a: int = 0
            b: int = 0
        
        foo = Foo()

        data = asdict(foo, exclude=["a"])
        assert list(data.keys()) == ["b"]

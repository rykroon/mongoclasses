from dataclasses import InitVar, dataclass, field
from typing import Any, ClassVar

from motor.motor_asyncio import AsyncIOMotorCollection
from mongoclasses import asdict, fromdict, is_mongoclass, _is_mongoclass_instance
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



class TestFromdict:

    """
    Tests for the fromdict() function.
    """

    def test_fromdict_success(self):
        @dataclass
        class Foo:
            a: int
            b: int
            c: int

        data = {"a": 1, "b": 2, "c": 3}
        obj = fromdict(Foo, data)
        assert isinstance(obj, Foo)

    def test_fromdict_success_recursive(self):
        @dataclass
        class Foo:
            x: int
        
        @dataclass
        class Bar:
            a: int
            b: Foo

        data = {"a": 1, "b": {"x": 1}}
        obj = fromdict(Bar, data)
        assert isinstance(obj.b, Foo)

    def test_not_a_class(self):
        @dataclass
        class Foo:
            a: int
            b: int
            c: int

        data = {"a": 1, "b": 2, "c": 3}
        with pytest.raises(TypeError):
            obj = fromdict(Foo(a=1, b=2, c=3), data)

    def test_missing_data_with_default(self):
        @dataclass
        class Foo:
            a: int
            b: int
            c: int = 0

        data = {"a": 1, "b": 2}
        obj = fromdict(Foo, data)
        assert obj.c == 0
    
    def test_missing_data_with_default_factory(self):
        @dataclass
        class Foo:
            a: int
            b: int
            c: list = field(default_factory=list)

        data = {"a": 1, "b": 2}
        obj = fromdict(Foo, data)
        assert obj.c == []

    def test_missing_data_without_default(self):
        @dataclass
        class Foo:
            a: int
            b: int
            c: int

        data = {"a": 1, "b": 2}
        with pytest.raises(TypeError):
            obj = fromdict(Foo, data)

    def test_extra_data(self):
        """
        Extra data should be ignored.
        """

        @dataclass
        class Foo:
            a: int
            b: int
            c: int

        data = {"a": 1, "b": 2, "c": 3, "d": 4}
        obj = fromdict(Foo, data)

    def test_initvars(self):
        """
        Make sure initvars are handled appropriately.
        """

        @dataclass
        class Foo:
            a: int
            b: int
            c: int
            d: InitVar[int]

        data = {"a": 1, "b": 2, "c": 3}

        with pytest.raises(TypeError):
            obj = fromdict(Foo, data)

        data["d"] = 4
        obj = fromdict(Foo, data)

    def test_non_init_fields(self):
        @dataclass
        class Foo:
            a: int
            b: int
            c: int
            d: int = field(init=False)

        data = {"a": 1, "b": 2, "c": 3}
        obj = fromdict(Foo, data)
        with pytest.raises(AttributeError):
            obj.d

        data["d"] = 4
        obj = fromdict(Foo, data)

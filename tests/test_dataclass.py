from dataclasses import InitVar, dataclass, field
from typing import Any, ClassVar

from motor.motor_asyncio import AsyncIOMotorCollection
from mongoclasses import (
    fromdict,
    is_mongoclass,
    is_mongoclass_instance,
    is_mongoclass_type,
)
import pytest


class TestIsMongoclass:

    """
    Tests for the is_mongoclass(), is_mongoclass_instance(),
    and is_mongoclass_type() functions.
    """

    def test_not_a_dataclass(self):
        class MyClass:
            ...

        assert is_mongoclass_type(MyClass) is False
        assert is_mongoclass_type(MyClass()) is False

        assert is_mongoclass_instance(MyClass) is False
        assert is_mongoclass_instance(MyClass()) is False

        assert is_mongoclass(MyClass) is False
        assert is_mongoclass(MyClass()) is False

    def test_no_id_and_no_collection(self):
        @dataclass
        class MyClass:
            ...

        assert is_mongoclass_type(MyClass) is False
        assert is_mongoclass_type(MyClass()) is False

        assert is_mongoclass_instance(MyClass) is False
        assert is_mongoclass_instance(MyClass()) is False

        assert is_mongoclass(MyClass) is False
        assert is_mongoclass(MyClass()) is False

    def test_no_collection(self):
        @dataclass
        class MyClass:
            _id: Any = None

        assert is_mongoclass_type(MyClass) is False
        assert is_mongoclass_type(MyClass()) is False

        assert is_mongoclass_instance(MyClass) is False
        assert is_mongoclass_instance(MyClass()) is False

        assert is_mongoclass(MyClass) is False
        assert is_mongoclass(MyClass()) is False

    def test_no_id(self):
        @dataclass
        class MyClass:
            collection: ClassVar[AsyncIOMotorCollection]

        assert is_mongoclass_type(MyClass) is False
        assert is_mongoclass_type(MyClass()) is False

        assert is_mongoclass_instance(MyClass) is False
        assert is_mongoclass_instance(MyClass()) is False

        assert is_mongoclass(MyClass) is False
        assert is_mongoclass(MyClass()) is False

    def test_incorrect_field_type_for_id(self):
        @dataclass
        class MyClass:
            collection: ClassVar[AsyncIOMotorCollection] = None
            _id: InitVar[Any] = None

        assert is_mongoclass_type(MyClass) is False
        assert is_mongoclass_type(MyClass()) is False

        assert is_mongoclass_instance(MyClass) is False
        assert is_mongoclass_instance(MyClass()) is False

        assert is_mongoclass(MyClass) is False
        assert is_mongoclass(MyClass()) is False

    def test_incorrect_field_type_for_collection(self):
        @dataclass
        class MyClass:
            collection: AsyncIOMotorCollection = None
            _id: Any = None

        assert is_mongoclass_type(MyClass) is False
        assert is_mongoclass_type(MyClass()) is False

        assert is_mongoclass_instance(MyClass) is False
        assert is_mongoclass_instance(MyClass()) is False

        assert is_mongoclass(MyClass) is False
        assert is_mongoclass(MyClass()) is False

    def test_success(self):
        @dataclass
        class MyClass:
            collection: ClassVar[AsyncIOMotorCollection] = None
            _id: Any = None

        assert is_mongoclass_type(MyClass) is True
        assert is_mongoclass_type(MyClass()) is False

        assert is_mongoclass_instance(MyClass) is False
        assert is_mongoclass_instance(MyClass()) is True

        assert is_mongoclass(MyClass) is True
        assert is_mongoclass(MyClass()) is True


class TestFromdict:

    """
    Tests for the fromdict() function.
    """

    def test_fromdict_basic(self):
        @dataclass
        class Foo:
            a: int
            b: int
            c: int

        data = {"a": 1, "b": 2, "c": 3}
        obj = fromdict(Foo, data)

    def test_not_a_dataclass(self):
        class Foo:
            a: int
            b: int
            c: int

        data = {"a": 1, "b": 2, "c": 3}
        with pytest.raises(TypeError):
            obj = fromdict(Foo, data)

    def test_not_a_class(self):
        @dataclass
        class Foo:
            a: int
            b: int
            c: int

        data = {"a": 1, "b": 2, "c": 3}
        with pytest.raises(TypeError):
            obj = fromdict(Foo(a=1, b=2, c=3), data)

    def test_missing_data(self):
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

        data["d"] = 4
        obj = fromdict(Foo, data)

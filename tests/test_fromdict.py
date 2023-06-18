from dataclasses import dataclass, field, InitVar
import pytest
from mongoclasses import fromdict


"""
    Test fromdict with complicated dataclasses.

    - Custom init method.
    - classes with initvars.
    - classes with some fields having init=False.
    - frozen dataclass.
    - data contains extra fields.
    - data does not contain all fields.
"""


class TestFromdict:

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
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


def test_fromdict_basic():
    @dataclass
    class Foo:
        a: int
        b: int
        c: int

    data = {"a": 1, "b": 2, "c": 3}
    obj = fromdict(Foo, data)


def test_fromdict_missing_data():
    @dataclass
    class Foo:
        a: int
        b: int
        c: int

    data = {"a": 1, "b": 2}
    with pytest.raises(TypeError):
        obj = fromdict(Foo, data)


def test_fromdict_extra_data():
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


def test_fromdict_initvars():
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


def test_fromdict_non_init_fields():
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
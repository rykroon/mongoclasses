from dataclasses import dataclass
from typing import Any

import pytest
from mongoclasses.update import to_update_expr, CurrentDate


def test_current_date():
    assert CurrentDate().value == {"$type": "date"}


class TestToUpdateExpr:

    def test_update_expr(self):
        @dataclass
        class Foo:
            x: Any
        
        f = Foo(x=CurrentDate())

        assert to_update_expr(f) == {"$currentDate": {"x": {"$type": "date"}}}

    def test_recursive_dataclass(self):
        @dataclass
        class Foo:
            x: Any
        
        f = Foo(x=Foo(x=0))

        assert to_update_expr(f) == {"$set": {"x.x": 0}}
    
    def test_list(self):
        @dataclass
        class Foo:
            x: Any
        
        f = Foo(x=[0, 1, 2])

        assert to_update_expr(f) == {"$set": {"x.0": 0, "x.1": 1, "x.2": 2}}
    
    def test_dict(self):
        @dataclass
        class Foo:
            x: Any
        
        f = Foo(x={"a": 1, "b": 2, "c": 3})

        assert to_update_expr(f) == {"$set": {"x.a": 1, "x.b": 2, "x.c": 3}}

from dataclasses import dataclass, is_dataclass, field
from typing import ClassVar

from pymongo import MongoClient
import pytest

from mongoclasses import is_mongoclass


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

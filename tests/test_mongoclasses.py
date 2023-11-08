from dataclasses import dataclass, field
from typing import ClassVar

from pymongo.collection import Collection

from mongoclasses import is_mongoclass


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

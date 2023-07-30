from dataclasses import dataclass, is_dataclass, field
from datetime import datetime

from pymongo import MongoClient
import pytest

from mongoclasses import mongoclass, is_mongoclass


@pytest.fixture
def client():
    return MongoClient()


class TestMongoclass:
    def test_not_a_class(self, client):
        with pytest.raises(TypeError):
            mongoclass(db=client["test"])(None)

    def test_missing_id_field(self, client):
        with pytest.raises(TypeError):

            @mongoclass(db=client["test"])
            class MyClass:
                ...

    def test_id_field_with_alias(self, client):
        # should not raise a TypeError.
        @mongoclass(db=client["test"])
        class MyClass:
            id: int = field(metadata={"mongoclasses": {"db_field": "_id"}})

    def test_make_dataclass(self, client):
        @mongoclass(db=client["test"])
        class MyClass:
            _id: int

        assert is_dataclass(MyClass) is True

    def test_default_collection_name(self, client):
        @mongoclass(db=client["test"])
        class MyClass:
            _id: int

        assert MyClass.__mongoclass_collection__.name == "myclass"

    def test_custom_collection_name(self, client):
        @mongoclass(db=client["test"], collection_name="my_class")
        class MyClass:
            _id: int

        assert MyClass.__mongoclass_collection__.name == "my_class"

    def test_auto_now_and_auto_now_add(self, client):
        with pytest.raises(ValueError):

            @mongoclass(db=client["test"], collection_name="my_class")
            class MyClass:
                _id: int
                created_at: datetime = field(
                    metadata={"mongoclasses": {"auto_now_add": True, "auto_now": True}}
                )

    def test_auto_now_with_default(self, client):
        with pytest.raises(ValueError):

            @mongoclass(db=client["test"], collection_name="my_class")
            class MyClass:
                _id: int
                created_at: datetime = field(
                    metadata={"mongoclasses": {"auto_now_add": True}},
                    default_factory=datetime.utcnow,
                )

    def test_auto_now_success(self, client):
        @mongoclass(db=client["test"], collection_name="my_class")
        class MyClass:
            _id: int
            created_at: datetime = field(
                metadata={"mongoclasses": {"auto_now_add": True}}
            )
            updated_at: datetime = field(metadata={"mongoclasses": {"auto_now": True}})


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
        @mongoclass(db=client["test"])
        class MyClass:
            _id: int = 0

        assert is_mongoclass(MyClass) is True
        assert is_mongoclass(MyClass()) is True

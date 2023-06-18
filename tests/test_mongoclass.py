from dataclasses import dataclass, InitVar
from typing import Any, ClassVar

from motor.motor_asyncio import AsyncIOMotorCollection
from mongoclasses import is_mongoclass, _is_mongoclass_instance, _is_mongoclass_type


class TestIsMongoclass:

    def test_not_a_dataclass(self):
        class MyClass:
            ...

        assert _is_mongoclass_type(MyClass) is False
        assert _is_mongoclass_type(MyClass()) is False

        assert _is_mongoclass_instance(MyClass) is False
        assert _is_mongoclass_instance(MyClass()) is False

        assert is_mongoclass(MyClass) is False
        assert is_mongoclass(MyClass()) is False

    def test_no_id_and_no_collection(self):
        @dataclass
        class MyClass:
            ...

        assert _is_mongoclass_type(MyClass) is False
        assert _is_mongoclass_type(MyClass()) is False

        assert _is_mongoclass_instance(MyClass) is False
        assert _is_mongoclass_instance(MyClass()) is False

        assert is_mongoclass(MyClass) is False
        assert is_mongoclass(MyClass()) is False


    def test_no_collection(self):
        @dataclass
        class MyClass:
            _id: Any = None

        assert _is_mongoclass_type(MyClass) is False
        assert _is_mongoclass_type(MyClass()) is False

        assert _is_mongoclass_instance(MyClass) is False
        assert _is_mongoclass_instance(MyClass()) is False

        assert is_mongoclass(MyClass) is False
        assert is_mongoclass(MyClass()) is False


    def test_no_id(self):
        @dataclass
        class MyClass:
            collection: ClassVar[AsyncIOMotorCollection]

        assert _is_mongoclass_type(MyClass) is False
        assert _is_mongoclass_type(MyClass()) is False

        assert _is_mongoclass_instance(MyClass) is False
        assert _is_mongoclass_instance(MyClass()) is False

        assert is_mongoclass(MyClass) is False
        assert is_mongoclass(MyClass()) is False
    
    def test_incorrect_field_type_for_id(self):
        @dataclass
        class MyClass:
            collection: ClassVar[AsyncIOMotorCollection] = None
            _id: InitVar[Any] = None

        assert _is_mongoclass_type(MyClass) is False
        assert _is_mongoclass_type(MyClass()) is False

        assert _is_mongoclass_instance(MyClass) is False
        assert _is_mongoclass_instance(MyClass()) is False

        assert is_mongoclass(MyClass) is False
        assert is_mongoclass(MyClass()) is False

    def test_incorrect_field_type_for_collection(self):
        @dataclass
        class MyClass:
            collection: AsyncIOMotorCollection = None
            _id: Any = None

        assert _is_mongoclass_type(MyClass) is False
        assert _is_mongoclass_type(MyClass()) is False

        assert _is_mongoclass_instance(MyClass) is False
        assert _is_mongoclass_instance(MyClass()) is False

        assert is_mongoclass(MyClass) is False
        assert is_mongoclass(MyClass()) is False
        

    def test_success(self):
        @dataclass
        class MyClass:
            collection: ClassVar[AsyncIOMotorCollection] = None
            _id: Any = None

        assert _is_mongoclass_type(MyClass) is True
        assert _is_mongoclass_type(MyClass()) is False

        assert _is_mongoclass_instance(MyClass) is False
        assert _is_mongoclass_instance(MyClass()) is True

        assert is_mongoclass(MyClass) is True
        assert is_mongoclass(MyClass()) is True

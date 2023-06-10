from dataclasses import dataclass
from typing import ClassVar, Optional


import pytest_asyncio
from motor.motor_asyncio import AsyncIOMotorClient

from mongoclasses import is_mongoclass, _is_mongoclass_instance, _is_mongoclass_type


@pytest_asyncio.fixture
async def collection():
    client = AsyncIOMotorClient()
    await client.drop_database('test')
    db = client['test']
    return db["test_collection"]


class TestIsMongoclassType:

    def test_not_a_dataclass(self):
        class MyClass:
            ...

        assert _is_mongoclass_type(MyClass) is False
        assert _is_mongoclass_type(MyClass()) is False

    def test_no_id_and_no_collection(self):
        @dataclass
        class MyClass:
            ...

        assert _is_mongoclass_type(MyClass) is False
        assert _is_mongoclass_type(MyClass()) is False


    def test_no_collection(self):
        @dataclass
        class MyClass:
            _id: Optional[str] = None

        assert _is_mongoclass_type(MyClass) is False
        assert _is_mongoclass_type(MyClass()) is False


    def test_no_id(self):
        @dataclass
        class MyClass:
            collection: ClassVar[str]

        assert _is_mongoclass_type(MyClass) is False
        assert _is_mongoclass_type(MyClass()) is False

    def test_success(self):
        @dataclass
        class MyClass:
            collection: ClassVar[str]
            _id: Optional[str] = None

        assert _is_mongoclass_type(MyClass) is True
        assert _is_mongoclass_type(MyClass()) is False

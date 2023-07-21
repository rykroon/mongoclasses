from dataclasses import dataclass
from typing import Any

from mongoclasses import mongoclass, is_mongoclass, _is_mongoclass_instance


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

    # def test_no_collection(self):
    #     @dataclass
    #     class MyClass:
    #         _id: Any = None
        
    #     assert is_mongoclass(MyClass) is False
    #     assert is_mongoclass(MyClass()) is False

    #     assert _is_mongoclass_instance(MyClass) is False
    #     assert _is_mongoclass_instance(MyClass()) is False

    # def test_no_id(self):
    #     @dataclass
    #     class MyClass:
    #         collection: ClassVar[AsyncIOMotorCollection]
        
    #     assert is_mongoclass(MyClass) is False
    #     assert is_mongoclass(MyClass()) is False

    #     assert _is_mongoclass_instance(MyClass) is False
    #     assert _is_mongoclass_instance(MyClass()) is False

    # def test_incorrect_field_type_for_id(self):
    #     @dataclass
    #     class MyClass:
    #         collection: ClassVar[AsyncIOMotorCollection] = None
    #         _id: InitVar[Any] = None
        
    #     assert is_mongoclass(MyClass) is False
    #     assert is_mongoclass(MyClass()) is False

    #     assert _is_mongoclass_instance(MyClass) is False
    #     assert _is_mongoclass_instance(MyClass()) is False

    # def test_incorrect_field_type_for_collection(self):
    #     @dataclass
    #     class MyClass:
    #         collection: AsyncIOMotorCollection = None
    #         _id: Any = None
        
    #     assert is_mongoclass(MyClass) is False
    #     assert is_mongoclass(MyClass()) is False

    #     assert _is_mongoclass_instance(MyClass) is False
    #     assert _is_mongoclass_instance(MyClass()) is False

    # def test_success(self):
    #     @mongoclass()
    #     class MyClass:
    #         _id: Any = None
        
    #     assert is_mongoclass(MyClass) is True
    #     assert is_mongoclass(MyClass()) is True

    #     assert _is_mongoclass_instance(MyClass) is False
    #     assert _is_mongoclass_instance(MyClass()) is True

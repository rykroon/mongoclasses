from dataclasses import dataclass
from typing import ClassVar, Optional

from mongoclasses import is_mongoclass, _is_mongoclass_instance, _is_mongoclass_type


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

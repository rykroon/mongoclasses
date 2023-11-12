from dataclasses import dataclass
from typing import ClassVar
from typing_extensions import Annotated

from mongoclasses import FieldInfo


from mongoclasses.types import (
    is_dataclass_instance,
    is_dataclass_type,
    is_mongoclass,
    is_mongoclass_instance,
    is_mongoclass_type
)


def test_is_dataclass_not_a_dataclass():
    class NotDataclass:
        pass

    assert not is_dataclass_type(NotDataclass)
    assert not is_dataclass_instance(NotDataclass)


def test_is_dataclass():
    @dataclass
    class Dataclass:
        pass


    assert is_dataclass_type(Dataclass)
    assert not is_dataclass_type(Dataclass())

    assert not is_dataclass_instance(Dataclass)
    assert is_dataclass_instance(Dataclass())


def test_is_mongoclass_not_a_dataclass():
    class NotDataclass:
        pass

    assert not is_mongoclass(NotDataclass)
    assert not is_mongoclass(NotDataclass())


def test_is_mongoclass_no_collection():
    @dataclass
    class Mongoclass:
        pass

    assert not is_mongoclass(Mongoclass)
    assert not is_mongoclass(Mongoclass())


def test_is_mongoclass_collection_not_classvar():
    @dataclass
    class Mongoclass:
        collection: str = ""

    assert not is_mongoclass(Mongoclass)
    assert not is_mongoclass(Mongoclass())


def test_is_mongoclass_no_id():
    @dataclass
    class Mongoclass:
        collection: ClassVar[str]

    assert not is_mongoclass(Mongoclass)
    assert not is_mongoclass(Mongoclass())


def test_is_mongoclass():
    @dataclass
    class Mongoclass:
        collection: ClassVar[str]
        _id: str = ""

    assert is_mongoclass(Mongoclass)
    assert is_mongoclass(Mongoclass())

    assert is_mongoclass_type(Mongoclass)
    assert not is_mongoclass_type(Mongoclass())

    assert not is_mongoclass_instance(Mongoclass)
    assert is_mongoclass_instance(Mongoclass())


def test_is_mongoclass_annotated_id():
    @dataclass
    class Mongoclass:
        collection: ClassVar[str]
        id: Annotated[str, FieldInfo(db_field="_id")] = ""

    assert is_mongoclass(Mongoclass)
    assert is_mongoclass(Mongoclass())

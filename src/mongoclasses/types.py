from dataclasses import Field
from typing import Any, ClassVar, Protocol


class DataclassInstance(Protocol):
    __dataclass_fields__: ClassVar[dict[str, Field[Any]]]


class MongoclassInstance(DataclassInstance):
    __mongoclass_config__: ClassVar[Any]

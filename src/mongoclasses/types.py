from dataclasses import Field
from typing import Any, ClassVar, Dict, Protocol


class DataclassInstance(Protocol):
    __dataclass_fields__: ClassVar[Dict[str, Field]]


class MongoclassInstance(DataclassInstance):
    __mongoclass_config__: ClassVar[Any]

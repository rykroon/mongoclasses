from pydantic import TypeAdapter


def _get_type_adapter(t, /):
    pass


def to_document(obj, /):
    adapter = _get_type_adapter(type(obj))
    return adapter.dump_python(obj)


def from_document(cls, data):
    adapter = _get_type_adapter(cls)
    return adapter.validate(data)

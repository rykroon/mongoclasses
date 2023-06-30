from dataclasses import asdict
from .dataclass import fromdict, create_include_dict_factory


def insert_one(obj, /):
    document = asdict(obj)
    if document["_id"] is None:
        del document["_id"]

    result = type(obj).collection.insert_one(document)
    obj._id = result.inserted_id
    return result


def update_one(obj, /, fields=None):
    dict_factory = dict if fields is None else create_include_dict_factory(fields)
    document = asdict(obj, dict_factory=dict_factory)
    return type(obj).collection.update_one(
        filter={"_id": obj._id}, update={"$set": document}
    )


def delete_one(obj, /):
    return type(obj).collection.delete_one({"_id": obj._id})


def find_one(cls, /, query, fromdict=fromdict):
    """
    Return a single instance that matches the query on the mongoclass or None.
    """
    document = cls.collection.find_one(query)
    if document is None:
        return None
    return fromdict(cls, document)


def find(cls, /, query):
    """
    Performs a query on the mongoclass.
    Returns a DocumentCursor.
    """
    return cls.collection.find(filter=query)

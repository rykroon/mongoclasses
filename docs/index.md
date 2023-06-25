# Mongoclasses

A simple and light tool for storing and retrieving python dataclasses with MongoDB.


### Installation
```
pip install mongoclasses
```


### What is a Mongoclass?
A Mongoclass is simply a dataclass. There are no base classes nor any extra class decorators besides
the built-in dataclass decorator.

In order for a dataclass to be considered a mongoclass it must have the following two fields:

- A ClassVar field named 'collection'.
- A field named '_id'.


### Quick Example
```
from dataclasses import dataclass
from typing import ClassVar
import mongoclasses
from pymongo import MongoClient
from pymongo.collection import Collection

client = MongoClient()
db = client["db"]

@dataclass
class MyMongoclass:
    collection: ClassVar[Collection] = db["collection"]
    _id: int = None

assert mongoclasses.is_mongoclass(MyMongoclass) is True
obj = MyMongoclass()
mongoclasses.insert_one(obj)
```

### Features
- Async support using motor.
- includes the following Mongodb operations:
    - insert_one
    - update_one
    - delete_one
    - find_one
    - find

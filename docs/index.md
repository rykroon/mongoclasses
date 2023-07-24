# Mongoclasses

A simple and light tool for storing and retrieving python dataclasses with MongoDB.


### Installation
```
pip install mongoclasses
```


### What is a Mongoclass?
A Mongoclass is simply a dataclass. Use the `mongoclass` decorator to create a mongoclass.


### Quick Example
```
from mongoclasses import mongoclass, is_mongoclass, insert_one
from pymongo import MongoClient

client = MongoClient()
database = client["db"]

@mongoclass(database)
class MyMongoclass:
    _id: int = None

assert is_mongoclass(MyMongoclass) is True
obj = MyMongoclass()
insert_one(obj)
```

### Features
- Async support using motor.
- includes the following Mongodb operations:
    - insert_one
    - update_one
    - delete_one
    - find_one
    - find

# Mongoclasses

Python dataclasses meets MongoDB.


### Installation
```
pip install mongoclasses
```


### What is a Mongoclass?
A Mongoclass is simply a dataclass with a few extra features related to MongoDB.


### Quick Example
```
from mongoclasses import mongoclass, is_mongoclass, insert_one
from pymongo import MongoClient

client = MongoClient()
db = client["db"]

@mongoclass(db=db)
class MyMongoclass:
    _id: int = None

assert is_mongoclass(MyMongoclass) is True
obj = MyMongoclass()
result = insert_one(obj)
```

### Features
- Async support using motor.
- includes the following Mongodb operations:
    - insert_one
    - replace_one
    - update_one
    - delete_one
    - find_one
    - find
    - create_indexes

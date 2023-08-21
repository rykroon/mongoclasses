
# Field Update Operators
# https://www.mongodb.com/docs/manual/reference/operator/update-field/#field-update-operators

def current_date(arg=None, /, **kwargs):
    return {"$currentDate": kwargs if arg is None else dict(arg, **kwargs)}


def inc(arg=None, /, **kwargs):
    return {"$inc": kwargs if arg is None else dict(arg, **kwargs)}


def min(arg=None, /, **kwargs):
    return {"$min": kwargs if arg is None else dict(arg, **kwargs)}


def max(arg=None, /, **kwargs):
    return {"$max": kwargs if arg is None else dict(arg, **kwargs)}


def mul(arg=None, /, **kwargs):
    return {"$mul": kwargs if arg is None else dict(arg, **kwargs)}


def rename(arg=None, /, **kwargs):
    return {"$rename": kwargs if arg is None else dict(arg, **kwargs)}


def set(arg=None, /, **kwargs):
    return {"$set": kwargs if arg is None else dict(arg, **kwargs)}


def set_on_insert(arg=None, /, **kwargs):
    return {"$setOnInsert": kwargs if arg is None else dict(arg, **kwargs)}


def unset(arg=None, /, **kwargs):
    return {"$unset": kwargs if arg is None else dict(arg, **kwargs)}


# Array Update Operators
# https://www.mongodb.com/docs/manual/reference/operator/update-array/#array-update-operators

def add_to_set(arg=None, /, **kwargs):
    return {"$addToSet": kwargs if arg is None else dict(arg, **kwargs)}


def pop(arg=None, /, **kwargs):
    return {"$pop": kwargs if arg is None else dict(arg, **kwargs)}


def pull(arg=None, /, **kwargs):
    return {"$pull": kwargs if arg is None else dict(arg, **kwargs)}


def push(arg=None, /, **kwargs):
    return {"$push": kwargs if arg is None else dict(arg, **kwargs)}


def pull_all(arg=None, /, **kwargs):
    return {"$pulAll": kwargs if arg is None else dict(arg, **kwargs)}


# Update Operator Modifiers
# https://www.mongodb.com/docs/manual/reference/operator/update-array/#update-operator-modifiers

def each(values):
    return {"$each": values}


def position(num, /):
    return {"$position": num}


def slice(num, /):
    return {"$slice": num}


def sort(sort_specification, /):
    return {"$sort": sort_specification}


# Bitwise Update Operators
# https://www.mongodb.com/docs/manual/reference/operator/update-bitwise/#bitwise-update-operator

def bit(arg=None, /, **kwargs):
    return {"$bit": kwargs if arg is None else dict(arg, **kwargs)}

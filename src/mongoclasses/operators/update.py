
# Field Update Operators
# https://www.mongodb.com/docs/manual/reference/operator/update-field/#field-update-operators

def current_date(arg=None, /, **kwargs):
    """
    Returns:
        A dictionary representing an Update Document with a $currentDate operator.
    """
    return {"$currentDate": kwargs if arg is None else dict(arg, **kwargs)}

def set_current_date(*fields):
    """
    Helper method for setting fields to current date.
    """
    return current_date({f: True for f in fields})


def inc(arg=None, /, **kwargs):
    """
    Returns:
        A dictionary representing an Update Document with an $inc operator.
    """
    return {"$inc": kwargs if arg is None else dict(arg, **kwargs)}


def min(arg=None, /, **kwargs):
    """
    Returns:
        A dictionary representing an Update Document with a $min operator.
    """
    return {"$min": kwargs if arg is None else dict(arg, **kwargs)}


def max(arg=None, /, **kwargs):
    """
    Returns:
        A dictionary representing an Update Document with a $max operator.
    """
    return {"$max": kwargs if arg is None else dict(arg, **kwargs)}


def mul(arg=None, /, **kwargs):
    """
    Returns:
        A dictionary representing an Update Document with a $mul operator.
    """
    return {"$mul": kwargs if arg is None else dict(arg, **kwargs)}


def rename(arg=None, /, **kwargs):
    """
    Returns:
        A dictionary representing an Update Document with a $rename operator.
    """
    return {"$rename": kwargs if arg is None else dict(arg, **kwargs)}


def set(arg=None, /, **kwargs):
    """
    Returns:
        A dictionary representing an Update Document with a $set operator.
    """
    return {"$set": kwargs if arg is None else dict(arg, **kwargs)}


def set_on_insert(arg=None, /, **kwargs):
    """
    Returns:
        A dictionary representing an Update Document with a $setOnInsert operator.
    """
    return {"$setOnInsert": kwargs if arg is None else dict(arg, **kwargs)}


def unset(arg=None, /, **kwargs):
    """
    Returns:
        A dictionary representing an Update Document with a $unset operator.
    """
    return {"$unset": kwargs if arg is None else dict(arg, **kwargs)}


def unset_fields(*fields):
    """
    Helper method that calls unset() ...
    """
    return unset({f: "" for f in fields})


# Array Update Operators
# https://www.mongodb.com/docs/manual/reference/operator/update-array/#array-update-operators

def add_to_set(arg=None, /, **kwargs):
    """
    Returns:
        A dictionary representing an Update Document with an $addToSet operator.
    """
    return {"$addToSet": kwargs if arg is None else dict(arg, **kwargs)}


def pop(arg=None, /, **kwargs):
    """
    Returns:
        A dictionary representing an Update Document with a $pop operator.
    """
    return {"$pop": kwargs if arg is None else dict(arg, **kwargs)}


def pull(arg=None, /, **kwargs):
    """
    Returns:
        A dictionary representing an Update Document with a $pull operator.
    """
    return {"$pull": kwargs if arg is None else dict(arg, **kwargs)}


def push(arg=None, /, **kwargs):
    """
    Returns:
        A dictionary representing an Update Document with a $push operator.
    """
    return {"$push": kwargs if arg is None else dict(arg, **kwargs)}


def pull_all(arg=None, /, **kwargs):
    """
    Returns:
        A dictionary representing an Update Document with a $pullAll operator.
    """
    return {"$pullAll": kwargs if arg is None else dict(arg, **kwargs)}


# Update Operator Modifiers
# https://www.mongodb.com/docs/manual/reference/operator/update-array/#update-operator-modifiers

def each(values, /):
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
    """
    Returns:
        A dictionary representing an Update Document with a $bit operator.
    """
    return {"$bit": kwargs if arg is None else dict(arg, **kwargs)}


def bit_and(arg=None, /, **kwargs):
    d = kwargs if arg is None else dict(arg, **kwargs)
    d = {k: {"and": v} for k, v in d.items()}
    return bit(d)


def bit_or(arg=None, /, **kwargs):
    d = kwargs if arg is None else dict(arg, **kwargs)
    d = {k: {"or": v} for k, v in d.items()}
    return bit(d)


def bit_xor(arg=None, /, **kwargs):
    d = kwargs if arg is None else dict(arg, **kwargs)
    d = {k: {"xor": v} for k, v in d.items()}
    return bit(d)

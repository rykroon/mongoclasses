__version__ = "0.4.0"


"""
Goals for version 0.4.0

- Add 'asdict' parameter for inserts and updates.
- Possibly rename 'collection' classvar to 'mongodb_collection'.
    This way the name 'collection' isn't reserved.

- Additional documentation using mkdocs.
    -Disclaimer that each minor version may be backwards incompatible
        until version 1.0.0.

    - Show how mongoclasses can work well with other packages:
        - dacite (fromdict)
        - pydantic (pydantic dataclasses)

    - Show example of creating custom asdict_shallow() function.
    - Show example of choosing which fields to update using dict_factory.

"""

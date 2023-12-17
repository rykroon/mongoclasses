__version__ = "0.7.0"


"""
    Goals:
    - Potentially move type annotations back to a separate .pyi file.
    - Add smarter logic for from_document.

    - Where the hell do I put collection, indexes, and id field?
        - Torn between putting them in the class body or in a decorator.

    - Adding a mongoclass decorator
        - Pros:
            - Can add indexes and collection in the decorator.
            - Can check for id field in the decorator.
            - Can add a __mongoclasses__ attribute to the class. (better for typing)
            - Checking if a class is a mongoclass is as simple as checking if it has a
                __mongoclasses__ attribute.
        - Cons:
            - Need to have the end developer use a decorator.
            - Need to consider inheritance.
    
            
    - Adding class attributes in the class body
        - Pros:
            - No need for a decorator.
            - No need to consider inheritance.
            - Gives freedom to the end developer to add their own class attributes.

        - Cons:
            - Can't check for id field upon dataclass creation.
            - Can't add a __mongoclasses__ attribute to the class. (worse for typing)
            - Potential naming conflicts with 'collection', and 'indexes'
            - Checking if a class is a mongoclass is more complicated.

    
    Additional notes:
        - Which is more pythonic?
            - I feel like doing any sort of type checking is not pythonic since type
                hints are not meant for runtime.
            - 
    
            
    I think I am leaning towards having two different ways to create a mongoclass:
        - Using a decorator that adds a __mongoclass_config__ attribute.
        - Allowing the developer to ad a mongoclass_config class attribute.

    As long as I have general methods like
        - get_collection
        - get_indexes
        - get_id_field
        - is_mongoclass
    then either way should work.

    Examples:

    @mongoclass(db=my_db, collection_name="myclass", indexes=[])
    class MyClass:
        # the decorator will add a __mongoclass_config__ attribute to the class.
        ...

    @dataclass
    class MyClass:
        mongoclass_config: ClassVar[MongoclassConfig] = MongoclassConfig()
        ...
"""

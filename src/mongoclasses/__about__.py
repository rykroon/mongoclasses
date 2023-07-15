__version__ = "0.5.0"


"""
Goals for 0.5.0

- Add conversions.
    - Dbref
    - Consider how to handle sets, frozensets, Date, and Time.
    - Think of a way to handle legacy UUID binary fields.


- Add documentation on conversions.

    
- Potentially add specific update operators to update_one() such as set, unset,
    currentDate, etc.
    - For example, unset_none will do an unset for all values that are None.


- Add additional operations such as:
    - find_one_and_delete()
    - find_one_and_update()
    - insert_many()
"""

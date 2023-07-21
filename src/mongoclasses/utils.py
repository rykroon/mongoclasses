from dataclasses import fields
from functools import lru_cache


@lru_cache
def _get_id_field(dcls):
    for field in fields(dcls):
        if _get_db_name(field) == "_id":
            return field
    return None


def _get_db_name(field):
    """
    Get the db_name of the field. Defaults to the field name, but can be overridden
    to a custom db_name.
    """
    return field.metadata.get("mongoclasses", {}).get("db_name", field.name)
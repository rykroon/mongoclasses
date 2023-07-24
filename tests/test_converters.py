from dataclasses import dataclass, field
from datetime import datetime, date
from decimal import Decimal
import re
from uuid import UUID, uuid4

from bson import Binary, DatetimeMS, Decimal128, ObjectId, Regex, SON
import pytest

from mongoclasses import converter
from mongoclasses.converters import register_db_name_overrides

import logging

def test_register_db_name_overrides():
    @dataclass
    class Foo:
        name: str = field(metadata={"mongoclasses": {"db_name": "first_name"}})
    
    register_db_name_overrides(Foo)

    f = Foo(name="Fred")
    assert converter.unstructure(f) == {"first_name": "Fred"}


class TestConversions:

    def test_date(self):
        
        d = date.today()
        assert converter.unstructure(d) == datetime(
            year=d.year, month=d.month, day=d.day
        )

        logging.warning(converter.structure(datetime.utcnow(), date))
        assert converter.structure(datetime.utcnow(), date) == date.today()

    def test_datetime(self):
        d = datetime.utcnow()
        assert converter.structure(d, datetime) == d
        assert converter.structure(d.isoformat(), datetime) == d
        assert converter.structure(d.timestamp(), datetime) == d

        # converting from/ to DateTimeMS rounds to the nearest millisecond.
        dtms = converter.structure(DatetimeMS(d), datetime)
        assert dtms.date() == d.date()
        assert dtms.hour == d.hour
        assert dtms.minute == d.minute
        assert dtms.second == d.second

        with pytest.raises(TypeError):
            converter.structure(None, datetime)

    def test_decimal(self):
        """
        Decimal objects are not accepted by MongoDB.
        Must convert to and from Decimal128
        """
        d = Decimal("1.23")
        d128 = Decimal128("1.23")
        assert converter.unstructure(d) == d128
        assert converter.structure(d, Decimal) == d
        assert converter.structure(d128, Decimal) == d

        assert converter.structure("1.23", Decimal) == d
        assert converter.structure(1.23, Decimal) == Decimal.from_float(1.23)
        assert converter.structure(1, Decimal) == Decimal(1)

        with pytest.raises(TypeError):
            converter.structure(None, Decimal)
    
    def test_decimal128(self):
        d = Decimal("1.23")
        d128 = Decimal128("1.23")
        assert converter.structure(d128, Decimal128) == d128
        assert converter.structure(d, Decimal128) == d128

        with pytest.raises(TypeError):
            converter.structure(None, Decimal128)
    
    def test_frozenset(self):
        f = frozenset({1, 2, 3, 4, 5})
        lst = [1, 2, 3, 4, 5]

        assert converter.unstructure(f) == lst

        assert converter.structure(f, frozenset) == f
        assert converter.structure(lst, frozenset) == f

    def test_objectid(self):
        oid = ObjectId()
        assert converter.structure(oid, ObjectId) == oid
        assert converter.structure(str(oid), ObjectId) == oid

    def test_pattern(self):
        p = re.compile(".*")
        reg = Regex.from_native(p)
        assert converter.structure(p, re.Pattern) == p
        assert converter.structure(reg, re.Pattern) == p

        with pytest.raises(TypeError):
            converter.structure(None, re.Pattern)
    
    def test_regex(self):
        p = re.compile(".*")
        reg = Regex.from_native(p)
        assert converter.structure(reg, Regex) == reg
        assert converter.structure(p, Regex) == reg

        with pytest.raises(TypeError):
            converter.structure(None, Regex)
    
    def test_set(self):
        s = set({1, 2, 3, 4, 5})
        lst = [1, 2, 3, 4, 5]

        assert converter.unstructure(s) == lst

        assert converter.structure(s, set) == s
        assert converter.structure(lst, set) == s

    def test_son(self):
        s = SON({"a": 1})
        assert converter.structure(s, SON) == s
        assert converter.structure(dict(s), SON) == s

    def test_uuid(self):
        u = uuid4()
        assert converter.structure(u, UUID) == u
        assert converter.structure(str(u), UUID) == u
        assert converter.structure(u.int, UUID) == u
        assert converter.structure(Binary.from_uuid(u), UUID) == u

        with pytest.raises(TypeError):
            converter.structure(None, UUID)

from datetime import datetime
from decimal import Decimal
import re
from uuid import UUID, uuid4

from bson import Binary, Decimal128, ObjectId, Regex, SON
import pytest

from mongoclasses import converter


class TestConversions:

    def test_datetime(self):
        d = datetime.utcnow()
        assert converter.structure(d, datetime) == d
        assert converter.structure(d.isoformat(), datetime) == d
        assert converter.structure(d.timestamp(), datetime) == d
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

    def test_objectid(self):
        o = ObjectId()
        assert converter.structure(o, ObjectId) == o
        assert converter.structure(str(o), ObjectId) == o

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

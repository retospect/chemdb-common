"""Tests for chemdb.sort — sort-string parser."""

from __future__ import annotations

import pytest

from chemdb.sort import SortField, parse_sort

VALID = {"lcd", "pld", "sa", "vf", "name", "relevance"}


class TestParseSort:
    def test_empty(self):
        assert parse_sort("", VALID) == []

    def test_single_asc(self):
        fields = parse_sort("lcd", VALID)
        assert fields == [SortField("lcd", descending=False)]

    def test_single_desc(self):
        fields = parse_sort("!lcd", VALID)
        assert fields == [SortField("lcd", descending=True)]

    def test_multi(self):
        fields = parse_sort("!lcd,sa", VALID)
        assert fields == [
            SortField("lcd", descending=True),
            SortField("sa", descending=False),
        ]

    def test_relevance(self):
        fields = parse_sort("relevance", VALID)
        assert fields == [SortField("relevance", descending=False)]

    def test_unknown_raises(self):
        with pytest.raises(ValueError, match="Unknown sort field"):
            parse_sort("xyz", VALID)

    def test_to_sql(self):
        f = SortField("lcd", descending=True)
        assert f.to_sql() == "lcd DESC"

    def test_to_sql_asc(self):
        f = SortField("sa", descending=False)
        assert f.to_sql() == "sa ASC"

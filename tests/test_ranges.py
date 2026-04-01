"""Tests for chemdb.ranges — range-string parser."""

from __future__ import annotations

import pytest

from chemdb.ranges import RangeOp, parse_range


class TestParseRange:
    def test_exact(self):
        r = parse_range("5")
        assert r.op is RangeOp.EXACT
        assert r.value == 5.0

    def test_exact_negative(self):
        r = parse_range("-1.2")
        assert r.op is RangeOp.EXACT
        assert r.value == -1.2

    def test_closed_range(self):
        r = parse_range("3..9")
        assert r.op is RangeOp.CLOSED
        assert r.low == 3.0
        assert r.high == 9.0

    def test_closed_range_negative(self):
        r = parse_range("-1.5..0")
        assert r.op is RangeOp.CLOSED
        assert r.low == -1.5
        assert r.high == 0.0

    def test_open_lower(self):
        r = parse_range("5..")
        assert r.op is RangeOp.GTE
        assert r.low == 5.0

    def test_open_lower_decimal(self):
        r = parse_range("0.7..")
        assert r.op is RangeOp.GTE
        assert r.low == 0.7

    def test_open_upper(self):
        r = parse_range("..9")
        assert r.op is RangeOp.LTE
        assert r.high == 9.0

    def test_gt(self):
        r = parse_range(">5")
        assert r.op is RangeOp.GT
        assert r.value == 5.0

    def test_lt(self):
        r = parse_range("<12")
        assert r.op is RangeOp.LT
        assert r.value == 12.0

    def test_gte(self):
        r = parse_range(">=5")
        assert r.op is RangeOp.GTE
        assert r.low == 5.0

    def test_lte(self):
        r = parse_range("<=12")
        assert r.op is RangeOp.LTE
        assert r.high == 12.0

    def test_empty_raises(self):
        with pytest.raises(ValueError, match="Empty"):
            parse_range("")

    def test_garbage_raises(self):
        with pytest.raises(ValueError):
            parse_range("abc")

    def test_whitespace_stripped(self):
        r = parse_range("  5..10  ")
        assert r.op is RangeOp.CLOSED
        assert r.low == 5.0
        assert r.high == 10.0


class TestParsedRangeMatches:
    def test_exact_matches(self):
        r = parse_range("5")
        assert r.matches(5.0)
        assert not r.matches(5.1)

    def test_closed_matches(self):
        r = parse_range("3..9")
        assert r.matches(3.0)
        assert r.matches(6.0)
        assert r.matches(9.0)
        assert not r.matches(2.9)
        assert not r.matches(9.1)

    def test_gte_matches(self):
        r = parse_range("5..")
        assert r.matches(5.0)
        assert r.matches(100.0)
        assert not r.matches(4.9)

    def test_lte_matches(self):
        r = parse_range("..9")
        assert r.matches(9.0)
        assert r.matches(-100.0)
        assert not r.matches(9.1)

    def test_gt_matches(self):
        r = parse_range(">5")
        assert r.matches(5.1)
        assert not r.matches(5.0)

    def test_lt_matches(self):
        r = parse_range("<12")
        assert r.matches(11.9)
        assert not r.matches(12.0)


class TestToSqlClause:
    def test_exact_sql(self):
        clause, params = parse_range("5").to_sql_clause("lcd")
        assert "lcd = :lcd_eq" in clause
        assert params["lcd_eq"] == 5.0

    def test_closed_sql(self):
        clause, params = parse_range("3..9").to_sql_clause("lcd")
        assert "lcd >= :lcd_lo" in clause
        assert "lcd <= :lcd_hi" in clause
        assert params["lcd_lo"] == 3.0
        assert params["lcd_hi"] == 9.0

    def test_gt_sql(self):
        clause, params = parse_range(">5").to_sql_clause("sa")
        assert "sa > :sa_gt" in clause
        assert params["sa_gt"] == 5.0

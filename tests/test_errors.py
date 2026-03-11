"""Tests for chemdb.errors — rich exceptions."""

from __future__ import annotations

from chemdb.errors import (
    DbMissingError,
    IdNotFoundError,
    InvalidRangeError,
    NoResultsError,
)


def test_db_missing_markdown():
    e = DbMissingError("mofty")
    md = e.to_markdown()
    assert "mofty" in md
    assert "chemdb sync mofty" in md


def test_no_results_hint():
    e = NoResultsError()
    assert "broadening" in e.hint


def test_id_not_found():
    e = IdNotFoundError("XYZABC")
    md = e.to_markdown()
    assert "XYZABC" in md
    assert "name:" in md


def test_invalid_range():
    e = InvalidRangeError("lcd", "abc")
    md = e.to_markdown()
    assert "lcd" in md
    assert "3..9" in md

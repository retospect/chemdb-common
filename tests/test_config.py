"""Tests for chemdb.config."""

from __future__ import annotations

from pathlib import Path

from chemdb.config import ChemdbConfig, load_config


def test_default_config_sqlite():
    cfg = ChemdbConfig()
    url = cfg.engine_url("mofty")
    assert url.startswith("sqlite:///")
    assert "mofty.db" in url


def test_postgres_url():
    cfg = ChemdbConfig(db_url="postgresql://localhost/acatome")
    url = cfg.engine_url("mofty")
    assert url == "postgresql://localhost/acatome"
    assert cfg.is_postgres


def test_not_postgres():
    cfg = ChemdbConfig()
    assert not cfg.is_postgres


def test_load_missing_file(tmp_path):
    cfg = load_config(tmp_path / "nonexistent.toml")
    assert cfg.db_url == ""
    assert cfg.mp_api_key == ""


def test_load_from_toml(tmp_path):
    toml_file = tmp_path / "chemdb.toml"
    toml_file.write_text(
        '[db]\nurl = "postgresql://localhost/test"\n\n'
        '[materials_project]\napi_key = "test_key"\n'
    )
    cfg = load_config(toml_file)
    assert cfg.db_url == "postgresql://localhost/test"
    assert cfg.mp_api_key == "test_key"

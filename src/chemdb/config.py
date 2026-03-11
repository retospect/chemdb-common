"""Configuration for chemdb — loads ~/.config/acatome/chemdb.toml."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:  # Python < 3.11
    import tomli as tomllib  # type: ignore[no-redef]


_DEFAULT_CONFIG_PATH = Path.home() / ".config" / "acatome" / "chemdb.toml"
_DEFAULT_CACHE_DIR = Path.home() / ".cache" / "acatome" / "chemdb"


@dataclass
class ChemdbConfig:
    """Resolved chemdb configuration."""

    db_url: str = ""
    cache_dir: Path = field(default_factory=lambda: _DEFAULT_CACHE_DIR)
    mp_api_key: str = ""

    def engine_url(self, schema: str) -> str:
        """Return the DB URL for a given schema (mofty / catapult).

        For Postgres: uses the configured URL (schema set via schema_translate_map).
        For SQLite: returns a per-schema file path.
        """
        if self.db_url:
            return self.db_url
        # Default: SQLite file per schema
        db_file = self.cache_dir / f"{schema}.db"
        return f"sqlite:///{db_file}"

    @property
    def is_postgres(self) -> bool:
        return self.db_url.startswith("postgresql")


def load_config(path: Path | None = None) -> ChemdbConfig:
    """Load config from TOML file + environment overrides."""
    path = path or _DEFAULT_CONFIG_PATH
    data: dict = {}
    if path.exists():
        data = tomllib.loads(path.read_text())

    db_section = data.get("db", {})
    mp_section = data.get("materials_project", {})
    local_section = data.get("local", {})

    db_url = db_section.get("url", os.environ.get("CHEMDB_DB_URL", ""))
    cache_dir = Path(
        local_section.get(
            "path", os.environ.get("CHEMDB_CACHE_DIR", str(_DEFAULT_CACHE_DIR))
        )
    ).expanduser()
    mp_api_key = mp_section.get("api_key", os.environ.get("MP_API_KEY", ""))

    return ChemdbConfig(db_url=db_url, cache_dir=cache_dir, mp_api_key=mp_api_key)

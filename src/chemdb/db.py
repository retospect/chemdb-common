"""Database engine factory — Postgres or SQLite from config."""

from __future__ import annotations

from sqlalchemy import create_engine, event, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from chemdb.config import ChemdbConfig


def make_engine(config: ChemdbConfig, schema: str) -> Engine:
    """Create a SQLAlchemy engine for the given schema.

    For Postgres: sets ``schema_translate_map`` so models with
    ``__table_args__ = {"schema": "mofty"}`` resolve correctly.

    For SQLite: enables WAL mode and ignores schema prefixes.
    """
    url = config.engine_url(schema)

    kwargs: dict = {}
    if config.is_postgres:
        kwargs["execution_options"] = {"schema_translate_map": {schema: schema}}
    else:
        # SQLite: map schema names to None so DDL drops the prefix
        kwargs["execution_options"] = {"schema_translate_map": {schema: None}}

    engine = create_engine(url, **kwargs)

    # SQLite: enable WAL mode for concurrent reads
    if url.startswith("sqlite"):

        @event.listens_for(engine, "connect")
        def _set_sqlite_pragma(dbapi_conn, connection_record):
            cursor = dbapi_conn.cursor()
            cursor.execute("PRAGMA journal_mode=WAL")
            cursor.execute("PRAGMA synchronous=NORMAL")
            cursor.close()

    return engine


def ensure_schema(engine: Engine, schema: str) -> None:
    """Create the Postgres schema if it doesn't exist (no-op for SQLite)."""
    if engine.url.get_backend_name() == "postgresql":
        with engine.connect() as conn:
            conn.execute(text(f"CREATE SCHEMA IF NOT EXISTS {schema}"))
            conn.commit()


def make_session(engine: Engine) -> sessionmaker[Session]:
    """Create a sessionmaker bound to the engine."""
    return sessionmaker(bind=engine)

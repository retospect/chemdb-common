"""chemdb CLI — downloads upstream data into local DB.

Usage:
    chemdb sync mofty
    chemdb sync catapult
    chemdb sync all
    chemdb status
"""

from __future__ import annotations

import typer

app = typer.Typer(help="Chemistry database management CLI")
sync_app = typer.Typer(help="Sync upstream chemistry databases to local storage")
app.add_typer(sync_app, name="sync")


@sync_app.command("mofty")
def sync_mofty(
    include_hmof: bool = typer.Option(
        False, "--include-hmof", help="Also pull hMOF (large)"
    ),
    force: bool = typer.Option(False, "--force", help="Rebuild from scratch"),
):
    """Sync MOF databases (CoRE, QMOF, CSD from MOFDB)."""
    from chemdb.config import load_config

    _sync_mofty(load_config(), include_hmof=include_hmof, force=force)


@sync_app.command("catapult")
def sync_catapult(
    force: bool = typer.Option(False, "--force", help="Rebuild from scratch"),
):
    """Sync catalysis databases (Catalysis-Hub)."""
    from chemdb.config import load_config

    _sync_catapult(load_config(), force=force)


@sync_app.command("all")
def sync_all(
    include_hmof: bool = typer.Option(
        False, "--include-hmof", help="Also pull hMOF (large)"
    ),
    force: bool = typer.Option(False, "--force", help="Rebuild from scratch"),
):
    """Sync all databases."""
    from chemdb.config import load_config

    config = load_config()
    _sync_mofty(config, include_hmof=include_hmof, force=force)
    _sync_catapult(config, force=force)


@app.command("status")
def status():
    """Show sync status for all databases."""
    from chemdb.config import load_config

    _show_status(load_config())


def _show_status(config):
    """Show last sync time, row counts, DB sizes."""
    from chemdb.db import make_engine

    for schema in ("mofty", "catapult"):
        try:
            engine = make_engine(config, schema)
            with engine.connect() as conn:
                # Try to read sync_log
                from sqlalchemy import text

                result = conn.execute(
                    text(
                        "SELECT source, synced_at, row_count FROM sync_log ORDER BY synced_at DESC LIMIT 5"
                    )
                )
                rows = result.fetchall()
                if rows:
                    typer.echo(f"\n{schema}:")
                    for row in rows:
                        typer.echo(f"  {row[0]}: {row[1]} ({row[2]} rows)")
                else:
                    typer.echo(f"\n{schema}: no sync history")
        except Exception:
            typer.echo(f"\n{schema}: not synced yet")


def _sync_mofty(config, *, include_hmof: bool, force: bool):
    """Sync MOF databases."""
    typer.echo("Syncing grandMOFty databases...")
    try:
        from grandmofty.db.sync import MoftySyncer

        syncer = MoftySyncer(config)
        syncer.run(include_hmof=include_hmof, force=force)
        typer.echo("✓ mofty sync complete")
    except ImportError:
        typer.echo(
            "grandmofty-mcp not installed. Run: pip install grandmofty-mcp",
            err=True,
        )
        raise typer.Exit(1)


def _sync_catapult(config, *, force: bool):
    """Sync catalyst databases."""
    typer.echo("Syncing CataPult databases...")
    try:
        from catapult.db.sync import CatapultSyncer

        syncer = CatapultSyncer(config)
        syncer.run(force=force)
        typer.echo("✓ catapult sync complete")
    except ImportError:
        typer.echo(
            "catapult-mcp not installed. Run: pip install catapult-mcp",
            err=True,
        )
        raise typer.Exit(1)


if __name__ == "__main__":
    app()

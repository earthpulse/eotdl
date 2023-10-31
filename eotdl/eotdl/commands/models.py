import typer
from pathlib import Path

from ..models import (
    retrieve_models,
    ingest_model,
    download_model,
)

app = typer.Typer()


@app.command()
def list(
    name: str = typer.Option(None, "--name", "-n", help="Filter by name"),
    limit: int = typer.Option(None, "--limit", "-l", help="Limit number of results"),
):
    try:
        models = retrieve_models(name, limit)
        typer.echo(models)
    except Exception as e:
        typer.echo(e)


@app.command()
def ingest(
    path: Path = typer.Option(..., "--path", "-p", help="Path to dataset"),
    verbose: bool = typer.Option(False, "--verbose", help="Verbose output"),
):
    try:
        ingest_model(path, verbose, typer.echo)
    except Exception as e:
        typer.echo(e)


@app.command()
def get(
    model: str,
    path: str = typer.Option(None, "--path", "-p", help="Download to a specific path"),
    version: int = typer.Option(None, "--version", "-v", help="Dataset version"),
    assets: bool = typer.Option(False, "--assets", "-a", help="Download assets"),
    force: bool = typer.Option(
        False, "--force", "-f", help="Force download even if file exists"
    ),
    verbose: bool = typer.Option(False, "--verbose", help="Verbose output"),
):
    try:
        dst_path = download_model(
            model, version, path, typer.echo, assets, force, verbose
        )
        typer.echo(f"Data available at {dst_path}")
    except Exception as e:
        typer.echo(e)


if __name__ == "__main__":
    app()

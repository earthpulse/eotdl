import typer
from pathlib import Path

from ..datasets import (
    retrieve_datasets,
    download_dataset,
    ingest_dataset,
)

app = typer.Typer()


@app.command()
def ingest(
    path: Path,
    f: bool = typer.Option(
        False, "--force", "-f", help="Force ingest even if file exists"
    ),
    d: bool = typer.Option(
        False, "--delete", "-d", help="Delete files not in the dataset"
    ),
):
    try:
        ingest_dataset(path, f, d, typer.echo)
    except Exception as e:
        typer.echo(e)


@app.command()
def list():
    datasets = retrieve_datasets()
    typer.echo(datasets)


@app.command()
def get(
    dataset: str,
    path: Path = typer.Option(None, "--path", "-p", help="Download to a specific path"),
    file: bool = typer.Option(None, "--file", "-f", help="Download a specific file"),
    assets: bool = typer.Option(False, "--assets", "-a", help="Download assets"),
    force: bool = typer.Option(
        False, "--force", "-f", help="Force download even if file exists"
    ),
):
    try:
        dst_path = download_dataset(dataset, file, path, typer.echo, assets, force)
        typer.echo(f"Data available at {dst_path}")
    except Exception as e:
        typer.echo(e)


if __name__ == "__main__":
    app()

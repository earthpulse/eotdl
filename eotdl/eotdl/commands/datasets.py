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
    f: bool = typer.Option(False, "--f", help="Force ingest even if file exists"),
    d: bool = typer.Option(False, "--d", help="Delete files not in the dataset"),
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
    path: str = None,
    file: str = None,
    assets: bool = False,
):
    try:
        dst_path = download_dataset(dataset, file, path, typer.echo, assets)
        typer.echo(f"Data available at {dst_path}")
    except Exception as e:
        typer.echo(e)


if __name__ == "__main__":
    app()

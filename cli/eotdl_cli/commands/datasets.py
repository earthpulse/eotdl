import typer
from src.usecases.datasets import (
    retrieve_datasets,
    download_dataset,
    update_dataset,
    ingest_large_dataset,
    ingest_large_dataset_parallel,
)
from src.usecases.auth import auth
from typing import Optional

app = typer.Typer()


@app.command()
def list():
    """
    List all datasets
    """
    datasets = retrieve_datasets()
    typer.echo(datasets)


@app.command()
def get(name: str, path: str = None):
    """
    Download a dataset

    name: Name of the dataset
    path: Path to download the dataset to
    """
    try:
        user = auth()
        dst_path = download_dataset(name, path, user, typer.echo)
        typer.echo(f"Dataset {name} downloaded to {dst_path}")
    except Exception as e:
        typer.echo(e)


@app.command()
def ingest(
    path: str,
    name: str,
    # p: Optional[int] = 0,
):
    """
    Ingest a dataset

    path: Path to dataset to ingest
    n: Name of the dataset
    """
    try:
        user = auth()
        # ingest_large_dataset_parallel(name, path, user, p, typer.echo)
        ingest_large_dataset(name, path, user, typer.echo)
        typer.echo(f"Dataset {name} ingested")
    except Exception as e:
        typer.echo(e)


@app.command()
def update(
    name: str,
    path: str,
):
    """
    Update a dataset

    name: Name of the dataset
    path: Path to dataset to ingest
    """
    try:
        user = auth()
        update_dataset(name, path, user, typer.echo)
        typer.echo(f"Dataset {name} updated")
    except Exception as e:
        typer.echo(e)


if __name__ == "__main__":
    app()

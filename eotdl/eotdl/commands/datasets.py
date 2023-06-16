import typer
from pathlib import Path

from ..datasets import (
    retrieve_datasets,
    download_dataset,
    update_dataset,
    ingest_file,
    ingest_folder,
    # ingest_large_dataset,
    # ingest_large_dataset_parallel,
)

app = typer.Typer()


@app.command()
def ingest(path: Path, name: str):
    """
    Ingest a dataset

    path: Path to dataset to ingest. Can be a file (.zip, .tar, .tar.gz, .csv, .txt, .json, .pdf, .md) or a directory (limited to 10 files, not recursive!)
    n: Name of the dataset
    """
    try:
        if path.is_dir():
            ingest_folder(path, name, typer.echo)
        else:
            ingest_file(name, path, typer.echo)
    except Exception as e:
        typer.echo(e)


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
        dst_path = download_dataset(name, path, typer.echo)
        typer.echo(f"Dataset {name} downloaded to {dst_path}")
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
        update_dataset(name, path, typer.echo)
        typer.echo(f"Dataset {name} updated")
    except Exception as e:
        typer.echo(e)


if __name__ == "__main__":
    app()

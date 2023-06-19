import typer
from pathlib import Path

from ..datasets import (
    retrieve_datasets,
    download_dataset,
    ingest_file,
    ingest_folder,
)

app = typer.Typer()


@app.command()
def ingest(path: Path, dataset: str):
    """
    Ingest a file

    path: Path to folder with data (limited to 10 files, not recursive!)
    dataset: Name of the dataset
    """
    try:
        if path.is_dir():
            ingest_folder(path, dataset, typer.echo)
        else:
            ingest_file(path, dataset, typer.echo)
    except Exception as e:
        typer.echo(e)


@app.command()
def list():
    """
    List all datasets and files
    """
    datasets = retrieve_datasets()
    typer.echo(datasets)


@app.command()
def get(dataset: str, file: str = None, path: str = None):
    """
    Download a dataset

    dataset: Name of the dataset
    file: Name of the file to download (optional, if not provided, the whole dataset will be downloaded)
    path: Path to download the dataset to (optional, if not provided, the dataset will be downloaded to ~/.eotdl/datasets)
    """
    try:
        dst_path = download_dataset(dataset, file, path, typer.echo)
        typer.echo(f"Data available at {dst_path}")
    except Exception as e:
        typer.echo(e)


if __name__ == "__main__":
    app()

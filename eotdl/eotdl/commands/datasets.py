import typer
from pathlib import Path

from ..datasets import (
    retrieve_datasets,
    download_dataset,
    ingest_folder,
    ingest_stac,
)

app = typer.Typer()


@app.command()
def ingest(
    path: Path,
    f: bool = typer.Option(False, "--f", help="Force ingest even if file exists"),
    d: bool = typer.Option(False, "--d", help="Delete files not in the dataset"),
):
    """
    Ingest a dataset

    path: Path to folder with the dataset
    """
    try:
        if not path.is_dir():
            typer.echo("Path must be a folder")
            return
        if "catalog.json" in [f.name for f in path.iterdir()]:
            ingest_stac(str(path) + "/catalog.json", typer.echo)
        else:
            ingest_folder(path, f, d, typer.echo)
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
def get(
    dataset: str,
    path: str = None,
    file: str = None,
):
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

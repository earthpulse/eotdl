import typer
from src.usecases.datasets import (
    retrieve_datasets,
    download_dataset,
    # ingest_dataset,
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
        dst_path = download_dataset(name, path, user)
        typer.echo(f"Dataset {name} downloaded to {dst_path}")
    except Exception as e:
        typer.echo(e)


# @app.command()
# def ingest(path: str):
#     """
#     Ingest a dataset

#     path: Path to dataset to ingest
#     """
#     try:
#         user = auth()
#         name = typer.prompt("Dataset name")
#         description = typer.prompt("Description")
#         # confirm
#         typer.confirm(f"Is the data correct?", abort=True)
#         ingest_dataset(name, description, path, user, typer.echo)
#         typer.echo(f"Dataset {name} ingested")
#     except Exception as e:
#         typer.echo(e)


@app.command()
def ingest(
    path: str,
    n: Optional[str] = None,
    d: Optional[str] = None,
    p: Optional[int] = 0,
):
    """
    Ingest a dataset

    path: Path to dataset to ingest
    n: Name of the dataset
    d: Description of the dataset
    p: Parallel ingest
    """
    try:
        user = auth()
        name = n or typer.prompt("Dataset name")
        description = d or typer.prompt("Description")
        # confirm
        if not n or not d:
            typer.confirm(f"Is the data correct?", abort=True)
        if p:
            ingest_large_dataset_parallel(name, description, path, user, p, typer.echo)
        else:
            ingest_large_dataset(name, description, path, user, typer.echo)
        typer.echo(f"Dataset {name} ingested")
    except Exception as e:
        typer.echo(e)


if __name__ == "__main__":
    app()

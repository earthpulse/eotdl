import typer
from src.usecases.datasets import (
    retrieve_datasets,
    download_dataset,
    ingest_dataset,
    ingest_large_dataset,
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
    y: Optional[bool] = False,
):
    """
    Ingest a dataset

    path: Path to dataset to ingest
    """
    try:
        user = auth()
        name = n or typer.prompt("Dataset name")
        description = d or typer.prompt("Description")
        # confirm
        if not y:
            typer.confirm(f"Is the data correct?", abort=True)
        ingest_large_dataset(name, description, path, user, typer.echo)
        typer.echo(f"Dataset {name} ingested")
    except Exception as e:
        typer.echo(e)


if __name__ == "__main__":
    app()

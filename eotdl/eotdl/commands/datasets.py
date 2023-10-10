import typer
from pathlib import Path

from ..datasets import (
    retrieve_datasets,
    ingest_dataset,
    # download_dataset,
)

app = typer.Typer()


@app.command()
def list(
    name: str = typer.Option(None, "--name", "-n", help="Filter by name"),
    limit: int = typer.Option(None, "--limit", "-l", help="Limit number of results"),
):
    try:
        datasets = retrieve_datasets(name, limit)
        typer.echo(datasets)
    except Exception as e:
        typer.echo(e)


@app.command()
def ingest(path: Path = typer.Option(..., "--path", "-p", help="Path to dataset")):
    try:
        ingest_dataset(path, typer.echo)
    except Exception as e:
        typer.echo(e)


# @app.command()
# def get(
#     dataset: str,
#     path: str = typer.Option(None, "--path", "-p", help="Download to a specific path"),
#     file: str = typer.Option(None, "--file", "-f", help="Download a specific file"),
#     assets: bool = typer.Option(False, "--assets", "-a", help="Download assets"),
#     force: bool = typer.Option(
#         False, "--force", "-f", help="Force download even if file exists"
#     ),
# ):
#     try:
#         dst_path = download_dataset(dataset, file, path, typer.echo, assets, force)
#         typer.echo(f"Data available at {dst_path}")
#     except Exception as e:
#         typer.echo(e)


# if __name__ == "__main__":
#     app()

import typer
from pathlib import Path

from ..models import (
    retrieve_models,
    ingest_model,
    download_model,
)

app = typer.Typer(help="Explore, ingest and download ML models.")


@app.command()
def list(
    name: str = typer.Option(
        None, "--name", "-n", help="Filter the returned models by name"
    ),
    limit: int = typer.Option(
        None, "--limit", "-l", help="Limit the number of returned results"
    ),
):
    """
    Retrieve a list with all the models in the EOTDL.

    If using --name, it will filter the results by name. If no name is provided, it will return all the models.\n
    If using --limit, it will limit the number of results. If no limit is provided, it will return all the models.
    \n\n
    Examples\n
    --------\n
    $ eotdl models list\n
    $ eotdl models list --name YourModel --limit 5
    """
    try:
        models = retrieve_models(name, limit)
        typer.echo(models)
    except Exception as e:
        typer.echo(e)


@app.command()
def ingest(
    path: Path = typer.Option(..., "--path", "-p", help="Path to the model to ingest"),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        help="Verbose output. This will print the progress of the ingestion",
    ),
):
    """
    Ingest a model to the EOTDL.

    This command ingests the model to the EOTDL. The model must be a folder with the model files,
    and at least a metadata.yml file or a catalog.json file. If there are not these files, the ingestion
    will not work. All the files in the folder will be uploaded to the EOTDL.
    \n\n
    The following constraints apply to the model name:\n
    - It must be unique\n
    - It must be between 3 and 45 characters long\n
    - It can only contain alphanumeric characters and dashes.\n
    \n
    The metadata.yml file must contain the following fields:\n
    - name: the name of the model\n
    - authors: the author or authors of the model\n
    - license: the license of the model\n
    - source: the source of the model\n
    \n
    If using --verbose, it will print the progress of the ingestion.
    \n\n
    Examples\n
    --------\n
    $ eotdl models ingest --path /path/to/folder-with-model --verbose True
    """
    try:
        ingest_model(path, verbose, typer.echo)
    except Exception as e:
        typer.echo(e)


@app.command()
def get(
    model: str = typer.Argument(None, help="Name of the model to download"),
    path: str = typer.Option(
        None, "--path", "-p", help="Download the model to a specific output path"
    ),
    file: str = typer.Option(
        None, "--file", "-f", help="Download a specific file from the model"
    ),
    version: int = typer.Option(None, "--version", "-v", help="Model version"),
    assets: bool = typer.Option(
        False, "--assets", "-a", help="Download STAC assets from the model"
    ),
    force: bool = typer.Option(
        False, "--force", "-f", help="Force download even if file exists"
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        help="Verbose output. This will print the progress of the download",
    ),
):
    """
    Download a model from the EOTDL.
    \n\n
    If using --path, it will download the model to the specified path. If no path is provided, it will download to ~/.eotdl/models.\n
    If using --file, it will download the specified file. If no file is provided, it will download the entire model.\n
    If using --version, it will download the specified version. If no version is provided, it will download the latest version.\n
    If using --assets when the model is STAC, it will also download the STAC assets of the model. If not provided, it will only download the STAC metadata.\n
    If using --force, it will download the model even if the file already exists.\n
    If using --verbose, it will print the progress of the download.
    \n\n
    Examples\n
    --------\n
    $ eotdl models get YourModel\n
    $ eotdl models get YourModel --path /path/to/download --file model.zip --version 1 --assets True --force True --verbose True
    """
    try:
        dst_path = download_model(
            model, version, path, typer.echo, assets, force, verbose
        )
        typer.echo(f"Data available at {dst_path}")
    except Exception as e:
        typer.echo(e)


if __name__ == "__main__":
    app()

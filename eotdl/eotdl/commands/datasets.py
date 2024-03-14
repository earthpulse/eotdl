import typer
from pathlib import Path

from ..datasets import (
    retrieve_datasets,
    ingest_dataset,
    download_dataset,
)

app = typer.Typer(help="Explore, ingest and download training datasets.")


@app.command()
def list(
    name: str = typer.Option(
        None, "--name", "-n", help="Filter the returned datasets by name"
    ),
    limit: int = typer.Option(
        None, "--limit", "-l", help="Limit the number of returned results"
    ),
):
    """
    Retrieve a list with all the datasets in the EOTDL.

    If using --name, it will filter the results by name. If no name is provided, it will return all the datasets.\n
    If using --limit, it will limit the number of results. If no limit is provided, it will return all the datasets.
    \n\n
    Examples\n
    --------\n
    $ eotdl datasets list\n
    $ eotdl datasets list --name YourModel --limit 5
    """
    try:
        datasets = retrieve_datasets(name, limit)
        typer.echo(datasets)
    except Exception as e:
        typer.echo(e)


@app.command()
def ingest(
    path: Path = typer.Option(
        ..., "--path", "-p", help="Path to the dataset to ingest"
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Verbose output. This will print the progress of the ingestion",
    ),
    foce_metadata_update: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Force metadata update even if it already exists. Will overwrite the current metadata in EOTDL",
    ),
    sync_metadata: bool = typer.Option(
        False,
        "--sync",
        "-s",
        help="Sync local metadata with the EOTDL. Will overwrite the local metadata",
    ),
):
    """
    Ingest a dataset to the EOTDL.

    This command ingests the dataset to the EOTDL. The dataset must be a folder with the dataset files,
    and at least a README.md file (and a catalog.json file for Q1+). If these files are missing, the ingestion
    will not work. All the files in the folder will be uploaded to the EOTDL.
    \n\n
    The following constraints apply to the dataset name:\n
    - It must be unique\n
    - It must be between 3 and 45 characters long\n
    - It can only contain alphanumeric characters and dashes.\n
    \n
    The README.md file must contain the following fields in the metadata header:\n
    - name: the name of the dataset\n
    - authors: the author or authors of the dataset\n
    - license: the license of the dataset\n
    - source: the source of the dataset\n
    - thumbnail: an image to use as the thumbnail of the dataset in the website\n
    The rest of the content in the README.md file will be used as the description of the dataset in the website.
    If using --verbose, it will print the progress of the ingestion.
    \n\n
    Examples\n
    --------\n
    $ eotdl dataset ingest --path /path/to/folder-with-dataset --verbose True
    """
    try:
        ingest_dataset(path, verbose, typer.echo, foce_metadata_update, sync_metadata)
    except Exception as e:
        typer.echo(e)


@app.command()
def get(
    dataset: str = typer.Argument(None, help="Name of the dataset to download"),
    path: str = typer.Option(
        None, "--path", "-p", help="Download the dataset to a specific output path"
    ),
    file: str = typer.Option(
        None, "--file", "-f", help="Download a specific file from the dataset"
    ),
    version: int = typer.Option(None, "--version", "-v", help="Dataset version"),
    assets: bool = typer.Option(
        False, "--assets", "-a", help="Download STAC assets from the dataset"
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
    Download a dataset from the EOTDL.
    \n\n
    If using --path, it will download the dataset to the specified path. If no path is provided, it will download to ~/.eotdl/datasets.\n
    If using --file, it will download the specified file. If no file is provided, it will download the entire dataset.\n
    If using --version, it will download the specified version. If no version is provided, it will download the latest version.\n
    If using --assets when the dataset is STAC, it will also download the STAC assets of the dataset. If not provided, it will only download the STAC metadata.\n
    If using --force, it will download the dataset even if the file already exists.\n
    If using --verbose, it will print the progress of the download.\n
    \n\n
    Examples\n
    --------\n
    $ eotdl dataset get YourDataset\n
    $ eotdl dataset get YourDataset --path /path/to/download --file dataset.zip --version 1 --assets True --force True --verbose True
    """
    try:
        dst_path = download_dataset(
            dataset,
            version,
            path,
            typer.echo,
            assets,
            force,
            verbose,
        )
        typer.echo(f"Data available at {dst_path}")
    except Exception as e:
        typer.echo(e)


if __name__ == "__main__":
    app()

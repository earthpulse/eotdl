import typer
from pathlib import Path

from ..fe import (
    ingest_openeo,
    retrieve_pipelines,
    stage_pipeline,
    deactivate_pipeline,
)

app = typer.Typer(help="Explore, ingest and download Feature Engineering Pipelines.")

@app.command()
def ingest(
    path: Path = typer.Option(..., "--path", "-p", help="Path to the pipeline to ingest"),
    verbose: bool = typer.Option(
        False,
        "--verbose",
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
    Ingest a pipeline to the EOTDL.

    This command ingests the pipeline to the EOTDL. The pipeline must be a folder with the pipeline files,
    and at least a README.md file. All the files in the folder will be uploaded to the EOTDL.
    \n\n
    Examples\n
    --------\n
    $ eotdl pipelines ingest --path /path/to/folder-with-pipeline --verbose True
    """
    try:
        ingest_openeo(path, verbose, typer.echo, foce_metadata_update, sync_metadata)
    except Exception as e:
        typer.echo(e)

@app.command()
def list(
    name: str = typer.Option(
        None, "--name", "-n", help="Filter the returned pipelines by name"
    ),
    limit: int = typer.Option(
        None, "--limit", "-l", help="Limit the number of returned results"
    ),
):
    """
    Retrieve a list with all the pipelines in the EOTDL.

    If using --name, it will filter the results by name. If no name is provided, it will return all the pipelines.\n
    If using --limit, it will limit the number of results. If no limit is provided, it will return all the pipelines.
    \n\n
    Examples\n
    --------\n
    $ eotdl pipelines list\n
    $ eotdl pipelines list --name YourPipeline --limit 5
    """
    try:
        pipelines = retrieve_pipelines(name, limit)
        typer.echo(pipelines)
    except Exception as e:
        typer.echo(e)

@app.command()
def get(
    pipeline: str = typer.Argument(None, help="Name of the pipeline to download"),
    path: str = typer.Option(
        None, "--path", "-p", help="Download the pipeline to a specific output path"
    ),
    version: int = typer.Option(None, "--version", "-v", help="pipeline version"),
    assets: bool = typer.Option(
        False, "--assets", "-a", help="Download STAC assets from the pipeline"
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
    Download a pipeline from the EOTDL.
    \n\n
    If using --path, it will download the pipeline to the specified path. If no path is provided, it will download to ~/.eotdl/pipelines.\n
    If using --version, it will download the specified version. If no version is provided, it will download the latest version.\n
    If using --assets when the pipeline is STAC, it will also download the STAC assets of the pipeline. If not provided, it will only download the STAC metadata.\n
    If using --force, it will download the pipeline even if the file already exists.\n
    If using --verbose, it will print the progress of the download.
    \n\n
    Examples\n
    --------\n
    $ eotdl pipelines get Yourpipeline\n
    $ eotdl pipelines get Yourpipeline --path /path/to/download  --version 1 --assets True --force True --verbose True
    """
    try:
        dst_path = stage_pipeline(
            pipeline, version, path, typer.echo, assets, force, verbose
        )
        typer.echo(f"Data available at {dst_path}")
    except Exception as e:
        typer.echo(e)


@app.command()
def delete(
    pipeline_name: str = typer.Argument(None, help="Name of the pipeline to delete")
):
    """
    Delete a model from the EOTDL.
    """
    try:
        deactivate_pipeline(pipeline_name)
        typer.echo(f"Pipeline {pipeline_name} deleted")
    except Exception as e:
        typer.echo(e)


if __name__ == "__main__":
    app()

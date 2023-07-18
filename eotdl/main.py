import typer
from eotdl.cli import app

__version__ = "2023.07.18"


def version():
    typer.echo(f" EOTDL Version: {__version__}")


if __name__ == "__main__":
    app.command()(version)
    app(prog_name="eotdl")

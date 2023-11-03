import typer
from .commands import auth, datasets, models
from . import __version__

app = typer.Typer(help="Welcome to EOTDL. Learn more at https://www.eotdl.com/")

app.add_typer(auth.app, name="auth")
app.add_typer(datasets.app, name="datasets")
app.add_typer(models.app, name="models")


@app.command()
def version():
    """
    Get EOTDL version.
    """
    typer.echo(f"EOTDL Version: {__version__}")


if __name__ == "__main__":
    app()

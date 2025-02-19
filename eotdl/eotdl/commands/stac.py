import typer

from ..curation.stac.api import api_status

app = typer.Typer(help="EOTDL STAC API")

@app.command()
def status():
    try:
        data = api_status()
        typer.echo(data)
    except Exception as e:
        typer.echo(e)
        raise typer.Abort()

import typer
from typing import Optional

from ..curation.stac.api import api_status, search_stac_columns, retrieve_stac_collections, retrieve_stac_collection, retrieve_stac_items, retrieve_stac_item, search_stac_items

app = typer.Typer(help="EOTDL STAC API")

@app.command()
def status():
    try:
        data = api_status()
        typer.echo(data)
    except Exception as e:
        typer.echo(e)
        raise typer.Abort()

@app.command()
def collections():
    try:
        data = retrieve_stac_collections()
        typer.echo(data)
    except Exception as e:
        typer.echo(e)
        raise typer.Abort()
    
@app.command()
def collection(collection_name: str):
    try:
        data = retrieve_stac_collection(collection_name)
        typer.echo(data)
    except Exception as e:
        typer.echo(e)
        raise typer.Abort()
    
@app.command()
def items(collection_id: str):
    try:
        data = retrieve_stac_items(collection_id)
        typer.echo(data)
    except Exception as e:
        typer.echo(e)

@app.command()
def item(collection_id: str, item_id: str):
    try:
        data = retrieve_stac_item(collection_id, item_id)
        typer.echo(data)
    except Exception as e:
        typer.echo(e)

@app.command()
def search(collection_id: str, query: Optional[str] = None):
    try:
        data = search_stac_items(collection_id, query)
        typer.echo(data)
    except Exception as e:
        typer.echo(e)
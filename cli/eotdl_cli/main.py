import typer
import os
import sys

# Add the eotdl_cli directory to the Python path
eotdl_cli_dir = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(eotdl_cli_dir))

from commands import auth, datasets

app = typer.Typer()
app.add_typer(auth.app, name="auth")
app.add_typer(datasets.app, name="datasets")

@app.command()
def hello(name: str = 'World!'):
    """Say hello to someone"""
    typer.echo(f"hello, {name}")

if __name__ == "__main__":
    app()
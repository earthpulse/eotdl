import typer
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
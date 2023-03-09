import typer
from commands import auth

app = typer.Typer()
app.add_typer(auth.app, name="auth")

@app.command()
def hello(name: str = 'World!'):
    """Say hello to someone"""
    typer.echo(f"hello, {name}")

if __name__ == "__main__":
    app()
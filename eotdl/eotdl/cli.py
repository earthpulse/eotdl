import typer
from .commands import auth, datasets

app = typer.Typer()

app.add_typer(auth.app, name="auth")
app.add_typer(datasets.app, name="datasets")

if __name__ == "__main__":
    app()

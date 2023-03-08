import typer

app = typer.Typer()


@app.callback()
def callback():
    pass


@app.command()
def hello(name: str = 'World!'):
    """Say hello to someone"""
    typer.echo(f"hello, {name}")

if __name__ == "__main__":
    app()
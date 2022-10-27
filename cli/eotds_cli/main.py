import typer
# from eotds.hello import hello

app = typer.Typer()


@app.callback()
def callback():
    """
    EOTDS CLI
    """


@app.command()
def hello():
    """
    Say hello
    """
    # data = hello()
    typer.echo("hello")

if __name__ == "__main__":
    app()
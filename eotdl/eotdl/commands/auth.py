import typer
from ..auth import is_logged, auth, logout_user
from ..auth.errors import LoginError

app = typer.Typer()


@app.command()
def login():
    try:
        user = auth()
        typer.echo(f"You are logged in as {user['email']}")
    except LoginError as e:
        typer.echo(e.message)
        raise typer.Exit(code=1)


@app.command()
def logout():
    user = is_logged()
    if user:
        typer.echo(f"You are logged in as {user['email']}")
        typer.confirm(f"Are you sure you want to logout?", abort=True)
        logout_url = logout_user()
        typer.echo(f"You are logged out.")
        typer.echo(
            f"If you want to login with a different account, visit {logout_url} and login again."
        )
    else:
        typer.echo(f"You are not logged in.")


if __name__ == "__main__":
    app()

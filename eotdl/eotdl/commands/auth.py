import typer
from ..auth import is_logged, auth, logout_user
from ..auth.errors import LoginError

app = typer.Typer(help="Login to EOTDL.")


@app.command()
def login():
    """
    Login to the EOTDL.

    This command will return a URL that you can visit to authenticate.
    After authentication, your credentials will be stored locally.
    This enables future commands to be executed without having to authenticate again
    (at least while the credentials are valid).
    \n\n
    The default browser will be opened automatically. If not, you can copy the URL and paste it in your browser.
    \n\n
    By default, the credentials will be stored in the following file: ~/.eotdl/credentials.json
    """
    try:
        user = auth()
        typer.echo(f"You are logged in as {user['email']}")
    except LoginError as e:
        typer.echo(e.message)
        raise typer.Exit(code=1)


@app.command()
def logout():
    """
    Logout from the EOTDL.

    You will receive a logout url that you can visit in case you want to authenticate with a different account.
    """
    user = is_logged()
    if user:
        typer.echo(f"You are logged in as {user['email']}")
        typer.confirm("Are you sure you want to logout?", abort=True)
        logout_url = logout_user()
        typer.echo("You are logged out.")
        typer.echo(
            f"If you want to login with a different account, visit {logout_url} and login again."
        )
    else:
        typer.echo("You are not logged in.")


if __name__ == "__main__":
    app()

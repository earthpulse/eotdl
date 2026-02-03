import os
from pathlib import Path
import typer

try:
    from dotenv import load_dotenv, find_dotenv  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    load_dotenv = None
    find_dotenv = None

from .commands import auth, datasets, models, stac, pipelines, challenges
from .repos import APIRepo
from . import __version__

def _load_dotenv_fallback():
    for parent in Path.cwd().resolve().parents:
        candidate = parent / ".env"
        if candidate.exists():
            for line in candidate.read_text().splitlines():
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, value = line.split("=", 1)
                key = key.strip()
                value = value.strip().strip('"').strip("'")
                if key and key not in os.environ:
                    os.environ[key] = value
            return


if load_dotenv and find_dotenv:
    load_dotenv(find_dotenv())
else:
    _load_dotenv_fallback()

app = typer.Typer(help="Welcome to EOTDL. Learn more at https://www.eotdl.com/")

app.add_typer(auth.app, name="auth")
app.add_typer(datasets.app, name="datasets")
app.add_typer(models.app, name="models")
app.add_typer(stac.app, name="stac")
app.add_typer(pipelines.app, name="pipelines")
app.add_typer(challenges.app, name="challenges")

@app.command()
def version():
    """
    Get EOTDL version.
    """
    typer.echo(f"EOTDL Version: {__version__}")


@app.command()
def api():
    """
    Get EOTDL API URL and info.
    """
    repo = APIRepo()
    typer.echo(f"EOTDL API URL: {repo.url}")
    typer.echo(repo.get_info())


if __name__ == "__main__":
    app()

import json
import os
from datetime import datetime, timezone
from pathlib import Path
import typer

from ..challenges import retrieve_challenges, submit_challenge

app = typer.Typer(help="Explore and submit AI4EO challenges.")


def _parse_datetime(value):
    if not value:
        return None
    if isinstance(value, datetime):
        return value
    try:
        return datetime.fromisoformat(value)
    except Exception:
        return None


def _status_from_dates(starts_at, ends_at):
    # Mirror philabchallenges web logic for active state.
    now = datetime.now(timezone.utc)
    if starts_at:
        starts_at = (
            starts_at if starts_at.tzinfo else starts_at.replace(tzinfo=timezone.utc)
        )
    if ends_at:
        ends_at = ends_at if ends_at.tzinfo else ends_at.replace(tzinfo=timezone.utc)
    active = (not ends_at or ends_at > now) and (not starts_at or starts_at < now)
    if active:
        return "active"
    if starts_at and starts_at > now:
        return "upcoming"
    return "ended"


def _normalize_tags(tags):
    if not tags:
        return []
    if isinstance(tags, str):
        return [t.strip() for t in tags.split(",") if t.strip()]
    return [str(t).strip() for t in tags if str(t).strip()]


@app.command("list")
def list_challenges():
    """
    List challenges from the Philabchallenges API.
    """
    try:
        if os.getenv("PHILABCHALLENGES_API_URL") is None:
            typer.echo(
                "Warning: PHILABCHALLENGES_API_URL is not set; using default http://localhost:8001/."
            )
        challenges = retrieve_challenges()
        output = []
        for c in challenges or []:
            starts_at = _parse_datetime(c.get("startsAt"))
            ends_at = _parse_datetime(c.get("endsAt"))
            output.append(
                {
                    "name": c.get("name"),
                    "title": c.get("title"),
                    "description": c.get("description"),
                    "prize": c.get("prize"),
                    "status": _status_from_dates(starts_at, ends_at),
                    "tags": _normalize_tags(c.get("tags")),
                }
            )
        typer.echo(json.dumps(output, indent=2))
    except Exception as e:
        typer.echo(e)


@app.command()
def submit(
    challenge: str = typer.Option(
        ..., "--challenge", "-c", help="Challenge name"
    ),
    file: Path = typer.Option(
        ..., "--file", "-f", help="Path to submission file"
    ),
    name: str = typer.Option(
        ..., "--name", "-n", help="Submission name"
    ),
    description: str = typer.Option(
        ..., "--description", "-d", help="Submission description"
    ),
):
    """
    Submit a file to a challenge (upload + notify scoring).
    """
    try:
        if os.getenv("PHILABCHALLENGES_API_URL") is None:
            typer.echo(
                "Warning: PHILABCHALLENGES_API_URL is not set; using default http://localhost:8001/."
            )
        submission_id = submit_challenge(
            challenge, file, name, description, typer.echo
        )
        typer.echo(f"Submission queued for scoring: {submission_id}")
    except Exception as e:
        typer.echo(e)


if __name__ == "__main__":
    app()

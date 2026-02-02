from pathlib import Path
import requests

from ..auth import with_auth
from ..repos import ChallengesAPIRepo


@with_auth
def submit_challenge(challenge, file_path, name, description, logger=print, user=None):
    if not user or "id_token" not in user:
        raise Exception(
            "Logto token required. Run `eotdl auth login` before submitting."
        )

    file_path = Path(file_path)
    if not file_path.exists():
        raise Exception(f"File not found: {file_path}")
    if not file_path.is_file():
        raise Exception(f"Path is not a file: {file_path}")

    repo = ChallengesAPIRepo()
    data, error = repo.create_submission(
        name, description, challenge, user, file_path.name
    )
    if error:
        raise Exception(error)

    presigned_url = data.get("presignedUrl") or data.get("presigned_url")
    submission_id = data.get("submissionId") or data.get("submission_id")
    if not presigned_url or not submission_id:
        raise Exception("Upload URL missing from response")

    logger("Uploading submission...")
    with open(file_path, "rb") as f:
        response = requests.put(presigned_url, data=f)
    if not response.ok:
        raise Exception("Failed to upload file")

    logger("Notifying scoring tool...")
    _, score_error = repo.notify_scoring(submission_id, challenge, user)
    if score_error:
        raise Exception(score_error)

    return submission_id

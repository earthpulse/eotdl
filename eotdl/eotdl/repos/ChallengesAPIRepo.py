import os
import requests

from .APIRepo import APIRepo


class ChallengesAPIRepo(APIRepo):
    def __init__(self, url=None):
        self._env_url = os.getenv("PHILABCHALLENGES_API_URL")
        self.url = url if url else os.getenv(
            "PHILABCHALLENGES_API_URL",
            "https://philabchallenges.api-dev.earthpulse.ai/",
        )
        if not self.url.endswith("/"):
            self.url += "/"

    @property
    def using_default_url(self):
        return self._env_url is None

    def list_challenges(self):
        response = requests.get(self.url + "challenges")
        return self.format_response(response)

    def get_challenge(self, challenge_id):
        response = requests.get(self.url + f"challenges/{challenge_id}")
        return self.format_response(response)

    def create_submission(self, name, description, challenge, user, filename=None):
        payload = {
            "name": name,
            "description": description,
            "challenge": challenge,
        }
        if filename:
            payload["filename"] = filename
        response = requests.post(
            self.url + "submissions/upload",
            json=payload,
            headers=self.generate_headers(user),
        )
        if response.status_code == 200:
            return response.json(), None
        detail = None
        try:
            detail = response.json().get("detail")
        except Exception:
            detail = response.text
        if response.status_code == 429:
            retry_after = response.headers.get("Retry-After")
            if retry_after:
                detail = f"{detail} Retry-After: {retry_after} seconds."
        return None, detail

    def notify_scoring(self, submission_id, challenge, user):
        response = requests.post(
            self.url + "submissions/score",
            json={"submission": submission_id, "challenge": challenge},
            headers=self.generate_headers(user),
        )
        if response.status_code == 200:
            return response.json(), None
        detail = None
        try:
            detail = response.json().get("detail")
        except Exception:
            detail = response.text
        return None, detail

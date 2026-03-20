from pathlib import Path
import importlib

from eotdl.repos.FilesAPIRepo import FilesAPIRepo


class _FakeResponse:
    def __init__(self, status_code=200, data=None, content=b""):
        self.status_code = status_code
        self._data = data or {}
        self.content = content

    def json(self):
        return self._data

    def raise_for_status(self):
        if self.status_code >= 400:
            raise Exception("HTTP error")


def test_stage_file_url_respects_output_name(monkeypatch, tmp_path):
    def _fake_get(url, headers=None):
        if "/stage/" in url:
            return _FakeResponse(
                status_code=200,
                data={"presigned_url": "https://storage.local/clearsar.ipynb-470630"},
            )
        if url == "https://storage.local/clearsar.ipynb-470630":
            return _FakeResponse(status_code=200, content=b"notebook-bytes")
        raise AssertionError(f"Unexpected URL: {url}")

    files_repo_module = importlib.import_module("eotdl.repos.FilesAPIRepo")
    monkeypatch.setattr(files_repo_module.requests, "get", _fake_get)

    repo = FilesAPIRepo(url="https://api.local/")
    file_path = repo.stage_file_url(
        "https://api.local/datasets/dataset-id/stage/clearsar.ipynb-470630",
        str(tmp_path),
        {"id_token": "token"},
        output_name="clearsar.ipynb",
    )

    assert file_path == str(tmp_path / "clearsar.ipynb")
    assert Path(file_path).read_bytes() == b"notebook-bytes"


def test_stage_file_url_keeps_legacy_name_without_output_name(monkeypatch, tmp_path):
    def _fake_get(url, headers=None):
        if "/stage/" in url:
            return _FakeResponse(
                status_code=200,
                data={"presigned_url": "https://storage.local/asset-999"},
            )
        if url == "https://storage.local/asset-999":
            return _FakeResponse(status_code=200, content=b"bytes")
        raise AssertionError(f"Unexpected URL: {url}")

    files_repo_module = importlib.import_module("eotdl.repos.FilesAPIRepo")
    monkeypatch.setattr(files_repo_module.requests, "get", _fake_get)

    repo = FilesAPIRepo(url="https://api.local/")
    file_path = repo.stage_file_url(
        "https://api.local/datasets/dataset-id/stage/asset-999",
        str(tmp_path),
        {"id_token": "token"},
    )

    assert file_path == str(tmp_path / "asset-999")
    assert Path(file_path).read_bytes() == b"bytes"

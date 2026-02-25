from pathlib import Path

from eotdl.files.metadata import Metadata


def test_save_metadata_supports_unicode_authors(tmp_path):
    metadata = Metadata(
        authors=["Janez Čuk", "María Šimek"],
        license="CC-BY-4.0",
        source="https://example.com",
        name="unicode-dataset",
        description="Unicode-safe description",
    )

    readme_path = Path(metadata.save_metadata(tmp_path))
    content = readme_path.read_text(encoding="utf-8")

    assert "Janez Čuk" in content
    assert "María Šimek" in content

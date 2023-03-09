from typer.testing import CliRunner

from eotdl_cli.main import app

runner = CliRunner()


def test_app():
    result = runner.invoke(app, ["hello", "--name", "test"])
    assert result.exit_code == 0
    assert "hello, test" in result.stdout


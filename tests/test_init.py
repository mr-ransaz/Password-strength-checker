import tomllib
from pathlib import Path

from pwcheck import __version__


def test_version_matches_project_metadata() -> None:
    root = Path(__file__).resolve().parents[1]
    with (root / "pyproject.toml").open("rb") as source:
        config = tomllib.load(source)
    assert __version__ == config["project"]["version"] == "0.1.0"
    assert config["project"]["requires-python"] == ">=3.14"
    assert config["project"]["dependencies"] == []

import ast
from pathlib import Path

import pytest

from pwcheck import __version__
from scripts import windows_version


def test_source_version_and_rendered_metadata() -> None:
    assert windows_version.package_version(windows_version.ROOT) == __version__
    resource = windows_version.version_resource(__version__)
    ast.parse(resource)
    assert f"StringStruct('FileVersion', {__version__!r})" in resource
    assert f"StringStruct('ProductVersion', {__version__!r})" in resource
    parts = tuple(map(int, __version__.split("."))) + (0,)
    assert f"filevers={parts!r}" in resource
    assert f"prodvers={parts!r}" in resource


@pytest.mark.parametrize(
    "version", ["", "1.2", "1.2.3.4", "1.2.3rc1", "x');raise RuntimeError", "65536.0.0"]
)
def test_invalid_version_cannot_create_a_resource(version: str) -> None:
    with pytest.raises(ValueError):
        windows_version.version_resource(version)


def test_version_generator_writes_and_prints(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    output = tmp_path / "nested/version.txt"
    assert windows_version.main(["--output", str(output)]) == 0
    assert output.read_text(encoding="utf-8") == windows_version.version_resource(
        __version__
    )
    assert windows_version.main(["--print-version"]) == 0
    assert capsys.readouterr().out.strip() == __version__


@pytest.mark.parametrize(
    "source", ['__version__ = "9.9.9"', 'unrelated = "0.1.1"', "__version__ = 123"]
)
def test_missing_or_mismatched_source_version(tmp_path: Path, source: str) -> None:
    package = tmp_path / "src/pwcheck"
    package.mkdir(parents=True)
    (package / "__init__.py").write_text(source, encoding="utf-8")
    (tmp_path / "pyproject.toml").write_text(
        '[project]\nversion="0.1.1"\n', encoding="utf-8"
    )
    with pytest.raises(ValueError):
        windows_version.package_version(tmp_path)

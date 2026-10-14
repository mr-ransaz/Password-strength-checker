import pytest

from pwcheck import hibp


@pytest.fixture(autouse=True)
def block_real_network(monkeypatch: pytest.MonkeyPatch) -> None:
    def forbidden(*args: object, **kwargs: object) -> None:
        raise AssertionError("Tests must mock HIBP; real network access is forbidden.")

    monkeypatch.setattr(hibp, "urlopen", forbidden)

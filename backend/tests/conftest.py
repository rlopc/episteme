import os

import pytest


@pytest.fixture(autouse=True)
def _clean_episteme_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    """Tests start without the EPISTEME_* variables that `just` and mise set."""
    for name in [name for name in os.environ if name.startswith("EPISTEME_")]:
        monkeypatch.delenv(name)
    # Safety net: no test may reach the real system keyring.
    monkeypatch.setenv("PYTHON_KEYRING_BACKEND", "keyring.backends.fail.Keyring")

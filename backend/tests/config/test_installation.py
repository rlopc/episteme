import json
from importlib import metadata
from typing import TYPE_CHECKING

import pytest

from episteme.config.errors import ConfigError
from episteme.config.installation import (
    DEFAULT_HOME,
    Environment,
    Installation,
    resolve_installation,
)

if TYPE_CHECKING:
    from pathlib import Path

FROM_REPO = json.dumps({"url": "file:///repo/backend", "dir_info": {"editable": True}})
FROM_WHEEL = json.dumps({"url": "file:///tmp/episteme.whl", "archive_info": {}})


def test_dev_installation_from_the_environment(tmp_path: Path) -> None:
    environ = {"EPISTEME_ENV": "dev", "EPISTEME_HOME": str(tmp_path)}

    assert resolve_installation(environ, FROM_REPO) == Installation(
        env=Environment.DEV, home=tmp_path
    )


def test_release_install_uses_the_default_home() -> None:
    assert resolve_installation({}, FROM_WHEEL) == Installation(
        env=Environment.USE, home=DEFAULT_HOME
    )


@pytest.mark.parametrize(
    "environ",
    [
        {},
        {"EPISTEME_ENV": "dev"},
        {"EPISTEME_HOME": "/nonexistent/episteme"},
        {"EPISTEME_ENV": "use", "EPISTEME_HOME": "/nonexistent/episteme"},
    ],
)
def test_run_from_the_repo_needs_the_dev_installation(environ: dict[str, str]) -> None:
    with pytest.raises(ConfigError, match="runs from a source folder"):
        resolve_installation(environ, FROM_REPO)


def test_release_install_may_set_its_home(tmp_path: Path) -> None:
    assert resolve_installation(
        {"EPISTEME_HOME": str(tmp_path)}, FROM_WHEEL
    ) == Installation(env=Environment.USE, home=tmp_path)


def test_reads_pep_610_metadata_of_this_install() -> None:
    # The test suite runs from the editable install of backend/.
    with pytest.raises(ConfigError, match="runs from a source folder"):
        resolve_installation({})


def test_unknown_environment_is_rejected(tmp_path: Path) -> None:
    with pytest.raises(ConfigError, match="EPISTEME_ENV is 'prod'"):
        resolve_installation({"EPISTEME_ENV": "prod", "EPISTEME_HOME": str(tmp_path)})


def test_relative_home_is_rejected() -> None:
    with pytest.raises(ConfigError, match="must be an absolute path"):
        resolve_installation(
            {"EPISTEME_ENV": "dev", "EPISTEME_HOME": ".dev"}, FROM_REPO
        )


class _Distribution:
    def __init__(self, direct_url: str | None) -> None:
        self._direct_url = direct_url

    def read_text(self, filename: str) -> str | None:
        assert filename == "direct_url.json"
        return self._direct_url


def test_install_without_pep_610_metadata_starts(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "episteme.config.installation.metadata.distribution",
        lambda _name: _Distribution(None),
    )

    assert resolve_installation({}).home == DEFAULT_HOME


def test_missing_distribution_starts(monkeypatch: pytest.MonkeyPatch) -> None:
    def missing(name: str) -> _Distribution:
        raise metadata.PackageNotFoundError(name)

    monkeypatch.setattr("episteme.config.installation.metadata.distribution", missing)

    assert resolve_installation({}).home == DEFAULT_HOME

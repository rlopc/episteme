"""Helpers for the API tests."""

from pathlib import Path
from typing import TYPE_CHECKING

from fastapi.testclient import TestClient
from pydantic import SecretStr

from episteme.adapters.hello_world_llm import HelloWorldLLM
from episteme.api.app import create_app
from episteme.application.chat import Chat
from episteme.application.orchestration.graph import build_graph
from episteme.config.installation import Environment, Installation
from episteme.config.settings import Config, Settings

if TYPE_CHECKING:
    from episteme.api.sessions import SessionStore

TOKEN = "test-token"  # noqa: S105 (fake token)
AUTH = {"Authorization": f"Bearer {TOKEN}"}


def make_client(
    env: Environment = Environment.USE,
    sessions: SessionStore | None = None,
    spa_dir: Path | None = None,
) -> TestClient:
    """A client of the hello-world app, sending episteme's own Host."""
    config = Config(
        installation=Installation(env=env, home=Path("/nonexistent")),
        settings=Settings.model_construct(),
    )
    chat = Chat(build_graph(HelloWorldLLM()))
    app = create_app(config, SecretStr(TOKEN), chat, sessions, spa_dir)
    return TestClient(
        app, base_url=f"http://127.0.0.1:{config.port}", follow_redirects=False
    )

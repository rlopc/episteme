---
status: accepted
date: 2026-11-20
---

# The project is renamed from ivlia to episteme

## Context and Problem Statement

The user renames the project, before the MVP, from ivlia to episteme: the repository, the Python package, the commands, the environment variables and the documentation. Inside the repository the rename is mechanical. Two things live outside it and hold the old name: the installation folder, `~/Library/Application Support/ivlia` (the default of `IVLIA_HOME`), and the macOS Keychain service `ivlia`, where the server keeps the API token it creates on its first start. What happens to them?

## Considered Options

- Document the move: the code uses only the new names, and the user moves the folder by hand.
- Migrate in code: when the old folder exists and the new one does not, the code moves it and copies the Keychain secret.
- Keep the old names for the folder and the Keychain service.

## Decision Outcome

Chosen option: document the move. Reasons:

- In phase 0 there is no real data in the installation, and a single user runs it, so migration code would run once and then stay as dead code.
- Keeping the old names would leave two names mixed in the code and the user's machine for good.

How it is applied:

- Everything versioned uses the new names: the package `episteme`, the commands `episteme` and `episteme-server`, the prefix `EPISTEME_` (`EPISTEME_HOME`, `EPISTEME_ENV`, `EPISTEME_API_TOKEN`), the default folder `~/Library/Application Support/episteme`, the Keychain service `episteme`, the cookies `episteme_session` and `episteme_session_dev`, and the repository `rlopc/episteme`.
- After the GitHub rename, the user moves the folder and deletes the old `ivlia` Keychain item by hand; the server creates a new API token under the `episteme` service on its first start.
- The user rebuilds the dev container. The three volumes renamed in `devcontainer.json` (`node_modules`, `frontend/node_modules`, `.venv`) are new and empty, and `post-create.sh` fills them again. Not verified: whether the Claude Code volume, `claude-code-config-${devcontainerId}`, is also new after the project folder moves; if it is, the Claude Code login, the GitHub MCP token file and the project memory have to be set up again.
- History is not rewritten: ADRs 0001 and 0002 keep the old name, and `CHANGELOG.md`, which release-please generates, is not edited by hand. `docs/00-indice.md` and `README.md` say the project was formerly ivlia.

### Consequences

- Good, because the code has no migration path to maintain.
- Bad, because an installation that is not moved by hand starts empty under the new folder, with a new API token.
- Bad, because the attestations of releases up to v0.1.2 name `rlopc/ivlia` in their certificates, and `gh attestation verify` compares repository names, so verifying those wheels needs the old name.

---
status: accepted
date: 2026-11-14
---

# Development happens in a dev container, not on the Mac

## Context and Problem Statement

Claude Code can edit any file in the repository, and some of those files run later with the user's full access: what the user runs with `!` (Playwright, `pnpm install`), their own commits (pre-commit runs tools from `.venv` and `node_modules`), `just setup`, and VS Code's extensions (mypy uses the `.venv`; ESLint loads `eslint.config.js`). On the Mac those processes run outside Claude Code's sandbox and can read the user's credentials and send them out ([docs/10](../../10-plan-y-pendientes.md), the row this ADR replaces). Where should the project's code run so that what Claude writes cannot reach the Mac?

## Considered Options

- Keep developing on the Mac and run every project command inside Claude Code's sandbox, with the files that run outside it denied to Claude.
- A separate standard macOS account for all development.
- Docker Sandboxes (`sbx`): a microVM per project, with the host repository read-only (clone mode), default-deny egress and a credential proxy.
- A dev container in Docker Desktop, attached from the Mac's VS Code.

## Decision Outcome

Chosen option: a dev container. Reasons:

- Every project command (Claude Code, the terminal, pre-commit, `just`, VS Code's language servers and extensions) runs inside the container, not on the Mac.
- It is the standard, mature way to define a reproducible development environment: an open specification that VS Code, GitHub Codespaces and the `devcontainer` CLI read.
- The sandbox-only option leaves the user's own commands and VS Code outside any boundary. The separate account was rejected on 2026-11-12 because of switching between sessions.
- Docker Sandboxes gives stronger isolation and was tried on 2026-11-14 (setup, checks, VS Code over Remote-SSH and the web chat all worked), but it is 0.x with breaking changes in each release, uses its own environment format (kits), puts Claude Code in `bypassPermissions` with its own instructions and hooks unless a custom kit replaces them, and keeps its data on the internal disk. Revisit it at 1.0 ([docs/10](../../10-plan-y-pendientes.md)).

How it is applied ([.devcontainer/](../../../.devcontainer/devcontainer.json), [repository.md](../../standards/repository.md#dev-container), [ai-development.md](../../standards/ai-development.md#bash-sandbox)):

- The project folder on the Mac is bind-mounted. `node_modules`, `frontend/node_modules` and `.venv` live in volumes: faster than the bind mount on macOS, and the Linux binaries never reach the host folder.
- `.devcontainer/` and `.vscode/` are mounted read-only inside the container, so nothing there can add an `initializeCommand`, which runs on the Mac, or poison the editor settings. They are edited on the Mac.
- Git is not used on the Mac for this repository: the container can write `.git/config` and `.git/hooks`, which the Mac's git would run (`core.fsmonitor`, hooks).
- The image adds only mise (the version in `mise.toml`) and Claude Code (stable channel). The tools come from `mise.lock`, which now covers Linux arm64.
- No egress firewall: the reference `init-firewall.sh` filters by IP once at start and breaks when CDN addresses rotate, and it is an example, not a maintained image.
- Claude Code's Bash sandbox is off inside the container: Docker's default seccomp profile blocks the user namespaces that bubblewrap needs.
- VS Code forwards the Mac's SSH agent, and the container pushes and signs with the user's key. VS Code has no setting that reliably stops the forwarding.

### Consequences

- Good, because nothing of the project runs on the Mac, and the Mac's credentials, files and Keychain are out of reach except through the bridges below.
- Good, because the environment is defined in versioned files, and the tools come from `mise.lock`. The base image follows its tag (image major 3), so a rebuild can pick up its patches; pinning it by digest is pending ([docs/10](../../10-plan-y-pendientes.md)).
- Bad, because the container has open network access, and Claude's commands are not sandboxed: prompt-injected code could send out what the container holds (the Claude Code login in `~/.claude`) or use the forwarded SSH agent while VS Code is attached. Permission rules, which match command text, and the GitHub ruleset on `main` remain the guards.
- Bad, because VS Code is a bridge by design: code in the container can use its extension API, and `$BROWSER` opens URLs on the Mac.
- Bad, because the parts of ivlia that depend on macOS (the models on the Mac's GPU, the Keychain, launchd) stay on the host; the next slices are re-evaluated against this setup ([docs/10](../../10-plan-y-pendientes.md)).

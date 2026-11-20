#!/usr/bin/env bash
# Runs once when the container is created: tools, dependencies and hooks.
set -euo pipefail

# New dependency volumes are owned by root.
sudo chown vscode:vscode node_modules frontend/node_modules .venv

mise trust
# just comes from mise.lock, and mise.toml turns off installing on first use.
mise install --locked
mise exec -- just setup
# The researcher hook runs ~/.local/bin/python3.14, the version in .python-version.
mise exec -- uv python install
# Chromium's system libraries, as in CI; they follow the Playwright version.
# sudo runs as root, whose mise has no tools: pass the PATH mise resolves for vscode.
tools_path="$(mise exec -- printenv PATH)"
sudo env "PATH=$tools_path" pnpm --filter episteme-frontend exec playwright install-deps chromium

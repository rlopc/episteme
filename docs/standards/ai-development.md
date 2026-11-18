# AI in development

Design: [docs/09](../09-ia-en-el-desarrollo.md).

## Instruction files

- [AGENTS.md](../../AGENTS.md): short; only what the AI cannot infer from the code (how to run `just check`, what not to touch without asking) and links to these standards.
- [CLAUDE.md](../../CLAUDE.md): imports `@AGENTS.md` and adds only what is specific to Claude Code.
- `.claude/rules/*.md`: rules per zone with a `paths:` list, which only link to this standards document. [backend.md](../../.claude/rules/backend.md) covers `backend/**` and [frontend.md](../../.claude/rules/frontend.md) covers `frontend/**`.
- No rule is duplicated: this standards document is the single source and is linked.

## Claude Code permissions

In [.claude/settings.json](../../.claude/settings.json). Precedence: deny, then ask, then allow. They apply the rules of no history rewriting, no deletion and no dependency changes without permission.

- Allow: `just` recipes except `just setup` and `just update-tools`; `uv run --locked`, `uv sync --locked --all-packages` (a partial `uv sync` would remove part of the shared `.venv`, so it asks); `pnpm install --frozen-lockfile`, `pnpm exec`, `pnpm run`; read-only git (`status`, `diff`, `log`, `show`, branch listing); `git add`, `git commit`, `git switch` and branch creation; and only `git remote get-url origin`; and the read tools of the `github` MCP server ([GitHub access](#github-access)). `just check` installs nothing: `uv run --locked` and `mise exec` use what `just setup` installed from `uv.lock` and `mise.lock`.
- Ask: `just setup`, `just update-tools`, `pnpm dlx`, `create`, `add`, `remove`, `update`; `uvx`, `uv add`, `uv remove`, `uv lock --upgrade`, `uv pip`, `uv tool`; `git push`, `rebase`, `commit --amend`, `reset`, `branch -d` and `-D`, `clean`, `git rm`, `git add -A`, `--all` and `.` (they would also stage the empty placeholder files the sandbox creates for protected paths); `rm`; `curl` and `wget`; the `github` MCP server's write tools; web tools.
- Deny: `git push --force` (also `-f` and `--force-with-lease`), `gh pr merge`, any push to `main`, and reading the use installation folder (`~/Library/Application Support/ivlia`), the secret folders listed in the file and the Claude Code login (`~/.claude/.credentials.json`) and the GitHub token (`~/.claude/github-mcp-token`); `security` (the Keychain); `Edit` on what Claude Code runs outside the sandbox and on its MCP configuration (the list is in [GitHub access](#github-access)), and on `.devcontainer/`, `.vscode/`, `.git/` and the user settings in the dev container's Claude volume (`~/.claude/settings.json`, `~/.claude/.claude.json`).
- Allow, ask and deny rules match the command text and can be bypassed. The real guards are the GitHub ruleset on `main` ([repository.md](repository.md#github)) and, in the dev container, the read-only mounts of `.devcontainer/` and `.vscode/` ([repository.md](repository.md#dev-container)).

## Bash sandbox

Development happens in the dev container ([ADR 0002](../decisions/adr/0002-dev-container.md)), and there the sandbox is **off**: Docker's default seccomp profile blocks the user namespaces that bubblewrap needs (checked on 2026-11-14: `unshare --user` fails with "Operation not permitted", and bubblewrap works only with `seccomp=unconfined`). The container's [managed settings](../../.devcontainer/managed-settings.json), copied to `/etc/claude-code/managed-settings.json` by the image, set `sandbox.enabled: false`; they outrank the project settings, and `/status` lists them as "Enterprise managed settings (file)". Revisiting it is in [docs/10](../10-plan-y-pendientes.md).

- Without the sandbox, Claude's commands have the container's open network, and `deny` rules on `Edit` stop only Claude's file tools, not a Bash command that writes the same file. What runs on the Mac (`.devcontainer/`) and what VS Code applies (`.vscode/`) is protected by mounting them read-only.
- `.claude/settings.json` keeps the sandbox configuration for any run outside the container: Bash writes only inside the project and the temporary directory and reaches only `github.com` and `api.github.com`; `autoAllowBashIfSandboxed: false`; `allowUnsandboxedCommands: false`; `excludedCommands` holds only `just setup` (also through `mise exec --`).
- Git and GitHub in the container: VS Code forwards the Mac's SSH agent, so `git push` and commit signing work from the container's terminal with the user's key (`gpg.format ssh` and a literal `key::` signing key, from the user's `.gitconfig` that VS Code copies). The user runs `git push`. `gh` is not installed in the container; the user runs it on the Mac with `--repo rlopc/ivlia`, which does not touch the working tree.

## GitHub access

Claude reads the repository's pull requests, runs, issues and alerts through GitHub's remote MCP server, which runs at GitHub: GitHub access adds only the `headersHelper` outside the sandbox, which follows the [Hooks](#hooks) rule, and the permission rules match tool names, not command text ([decision map](../decisions/README.md)). It is set up in the dev container; Claude is not run on the Mac in this repository.

- Server: `https://api.githubcopilot.com/mcp/readonly`, added by the user in Claude Code's user scope (`~/.claude/.claude.json` in the dev container's Claude volume, out of Claude's file tools), never in a versioned `.mcp.json`, which Claude could edit. No Copilot subscription was needed (checked on 2026-11-12).
- Credential: a fine-grained personal access token named `ivlia-dev-mcp`, "Only select repositories" with this repository, expiring after 90 days. The macOS Keychain (service `github-mcp-token`) keeps the user's copy; the container has no Keychain, so the token is also in `~/.claude/github-mcp-token` (mode 600) in the Claude volume, which survives rebuilds. [github-mcp-headers.sh](../../.claude/bin/github-mcp-headers.sh), installed by the user as `~/.claude/bin/github-mcp-headers`, also in the volume, is the server's `headersHelper`: Claude Code runs it when connecting and sends the headers it prints. It follows the [Hooks](#hooks) rule: `/bin/bash` and `PATH=/usr/bin:/bin`. The token is never in a versioned file or in Claude's context, but the file has the same exposure as the Claude Code login next to it: without the sandbox, a Bash command can read it, and a `Read` deny rule stops only Claude's file tools ([Bash sandbox](#bash-sandbox)). The token's narrow, read-only scope and its expiry limit the damage.
- Token permissions: read-only for now: Metadata, Contents, Pull requests, Issues, Actions, Commit statuses, Dependabot alerts and Code scanning alerts. Check runs are read without Checks, since the repository is public. The server is used at `/mcp/readonly`, so the user makes every write. Write access waits for a domain-based egress filter in the dev container ([docs/10](../10-plan-y-pendientes.md)); then Pull requests, Contents (merging needs it), Actions (re-run and cancel) and Issues get write access.
- Toolsets (header `X-MCP-Toolsets`): `context`, `issues`, `pull_requests`, `actions`, `dependabot`, `code_security`. Not `repos`, which writes files and branches and can delete repositories. Lockdown (`X-MCP-Lockdown`) hides content from users without push access, against injected instructions in a public repository; GitHub states it is a filter, not a security boundary.
- Permissions: read tools (`get_*`, `list_*`, `search_*`, `pull_request_read`, `issue_read`, `actions_get`, `actions_list`) are allowed; write tools (pull requests, issues, comments, reviews, merging, `actions_run_trigger`) ask. `actions_run_trigger` can also start workflows and delete run logs; Claude uses it only to re-run or cancel a run. Claude cannot edit what Claude Code runs outside the sandbox or its MCP configuration: `Edit` is denied on `~/.claude/bin/`, `~/.local/bin/`, `~/.local/share/uv/`, `~/.claude.json`, `~/.claude/.claude.json`, `.mcp.json`, `.claude/settings.json`, `.claude/settings.local.json` and `.claude/hooks/` (an `Edit` rule also covers writes; Claude Code warns that a `Write` rule never matches), and `Read` on `~/.claude/github-mcp-token`. In the dev container these rules, like the hook's, stop only Claude's file tools ([Bash sandbox](#bash-sandbox)).
- Once the server has write access, Claude merges a PR only when the user asks, with `merge_pull_request` and the squash method; the ruleset on `main` refuses it until the required checks pass.
- Claude does not push: the user runs `git push`. Dismissing a Dependabot alert has no MCP tool, so the user does it.
- The [`pr` skill](../../.claude/skills/pr/SKILL.md) is the procedure; while the server is read-only, the user makes the writes it describes.

Setup, once per dev container volume (by the user, from the repository root):

1. In GitHub, create the `release` environment, limited to `main`, with the release key ([release.md](release.md#credential)). Once the branch that adds `environment: release` is on `main`, delete the repository-level copy of the key; until then, `main`'s release workflow still reads it.
2. Create the token (Settings, Developer settings, Fine-grained tokens) with the permissions above, and keep it in the Mac's Keychain: `security add-generic-password -s github-mcp-token -a github-mcp -w`, pasting it at the prompt, never into a file or an editor.
3. On the Mac, copy it: `security find-generic-password -s github-mcp-token -w | pbcopy`. In the container's terminal, `(umask 077; read -rsp 'Token: ' t && printf '%s\n' "$t" > ~/.claude/github-mcp-token)`, paste at the prompt, then clear the Mac's clipboard with `pbcopy < /dev/null`.
4. In the container, read `.claude/bin/github-mcp-headers.sh`, then `install -D -m 755 .claude/bin/github-mcp-headers.sh ~/.claude/bin/github-mcp-headers`. Install it again, after reading the change, whenever it changes.
5. In the container, `claude mcp add-json --scope user github "{\"type\":\"http\",\"url\":\"https://api.githubcopilot.com/mcp/readonly\",\"headersHelper\":\"$HOME/.claude/bin/github-mcp-headers\"}"`, then restart Claude Code.

When the token expires, create a new one, replace it in the Keychain with `security add-generic-password -U -s github-mcp-token -a github-mcp -w`, repeat step 3, and reconnect the server from `/mcp`.

## Hooks

- PreToolUse on Bash: `researcher-bash-guard.py` limits the read-only Bash of the `researcher` agent. Its test (`.claude/hooks/researcher-bash-guard.test.sh`) runs in `just check`.
- Hooks run outside the Bash sandbox, with the user's permissions, and so does the `headersHelper` ([GitHub access](#github-access)). Rule: what Claude Code runs outside the sandbox runs only files with an absolute path that Claude cannot write, apart from the hook's own script in `.claude/hooks/`, which the sandbox and the `Edit` rules protect. Nothing from `.venv`, `node_modules` or the `PATH`, which starts with `node_modules/.bin` (`_.path` in `mise.toml`).
- The guard is standard-library Python. Claude Code starts it in the hook's exec form, without a shell of its own: `command` is `/bin/sh`, by absolute path, and `args` is `-c` with `exec "$HOME/.local/bin/python3.14" -I "$CLAUDE_PROJECT_DIR/.claude/hooks/researcher-bash-guard.py"`. `/bin/sh` only expands the two variables, so no program is looked up in the `PATH`. `~/.local/bin/python3.14` is the uv-managed Python of `.python-version`, which [post-create.sh](../../.devcontainer/post-create.sh) installs with `uv python install`. `Edit` is denied on `~/.local/bin/` and `~/.local/share/uv/`; in the dev container the sandbox is off, so these rules, like the ones on `.claude/hooks/`, stop only Claude's file tools. When `.python-version` changes its minor version, the hook's path changes with it. If the interpreter is missing, the hook fails and `onFailure: "block"` blocks every Bash command.
- The test runs the guard with the root `.venv`'s Python, the same version, because CI has no `~/.local/bin/python3.14`.
- No hook runs after edits: it would run the linters from `.venv` and `node_modules` outside the sandbox. pre-commit reports problems at commit; to check earlier, Claude runs `uv run --locked pre-commit run --files <files>`.

## Validar

Procedure in the skill [validar](../../.claude/skills/validar/SKILL.md) (Spanish until `.claude/` is translated), run before each step and slice.

- The `researcher` agent, with the Sonnet model, reads current official docs and versions (network use confirmed by the user) and compares them with the design, the plan and the repository.
- The report (confirmed, changed, risks, sources with how much was read) is saved in `.dev/validar-step-N.md` (gitignored) and shown to the user before work starts. Its summary goes in the PR description.
- Versions are checked against the 7-day cooldown ([README](README.md#versions-policy)).

## Reviewer

The [reviewer](../../.claude/agents/reviewer.md) agent (Opus, tools Read, Grep and Glob only, no network, clean context) reviews each branch before the user. After `just check` is green, `just review-diff` (or `just review-diff <parent-branch>` for a stacked PR) writes the diff and file list to `.dev/review/`; the reviewer reads them and reports findings by severity. The findings and how they were handled go in the PR.

## Other skills

- [research](../../.claude/skills/research/SKILL.md) (Spanish until `.claude/` is translated): queries the project's configured knowledge sources through `researcher` agents and synthesizes what they return.
- [pr](../../.claude/skills/pr/SKILL.md): pull requests through the `github` MCP server: create, update a stacked branch after a squash merge, checks and merge ([GitHub access](#github-access)).
- [review-file](../../.claude/skills/review-file/SKILL.md): explains one development tool or configuration file in junior-level terms and reviews it against the [Toolchain rules](repository.md#toolchain-rules).

## OpenSpec

- Run with `pnpm exec openspec` (version in [package.json](../../package.json)). Telemetry is off (`OPENSPEC_TELEMETRY=0`, `DO_NOT_TRACK=1` in the justfile).
- Initialized with `pnpm exec openspec init --tools claude`. Generated: `.claude/skills/openspec-*/` and `.claude/commands/opsx/`; after an upgrade, run `openspec update`. Edited by people: [openspec/config.yaml](../../openspec/config.yaml) and `openspec/specs/`.
- `just check` runs `openspec validate --all --strict`.
- Phase 0 is built without the OpenSpec cycle; the cycle is used from slice 2.

## AI per task

Provisional, from [docs/09](../09-ia-en-el-desarrollo.md) ("IA por tarea"): proposing, specifying and designing, the most capable model; implementing specified tasks, a faster model (Sonnet); independent review, a subagent with clean context (Opus); research, read-only subagents (Sonnet, Haiku for mechanical searches).

## Rules for the AI

- Quality tools guide it: it runs the checks through `just`, reads the errors and fixes them before the user reviews.
- It does not finish a task while a check fails, and does not disable or relax a rule to make it pass.
- It does not edit generated files by hand.

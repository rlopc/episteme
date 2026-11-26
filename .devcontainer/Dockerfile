# Development container for episteme. Tools come from mise.lock (postCreateCommand);
# the image only adds what mise cannot install.
FROM mcr.microsoft.com/devcontainers/base:3-ubuntu26.04

# Claude Code settings that apply only inside this container. Its Bash sandbox
# is off: Docker's default seccomp profile blocks the user namespaces it needs.
COPY managed-settings.json /etc/claude-code/managed-settings.json

USER vscode
# mise's shims give non-interactive shells (docker exec, bash -l -c, scripts and
# agents) the locked tools; the interactive bash still activates mise in .bashrc.
ENV PATH=/home/vscode/.local/bin:/home/vscode/.local/share/mise/shims:$PATH

# Same mise as min_version in mise.toml; mise.run verifies it against SHASUMS256.
RUN curl -fsSL https://mise.run | MISE_VERSION=v2026.11.5 sh \
    && echo 'eval "$(mise activate bash)"' >> /home/vscode/.bashrc

# Claude Code from the stable channel; it updates itself.
RUN curl -fsSL https://claude.ai/install.sh | bash -s stable

# Owned by vscode, so the Claude volume mounted here inherits the owner.
RUN mkdir -p /home/vscode/.claude

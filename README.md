# episteme

episteme (formerly ivlia) is a 100 % local personal AI assistant that manages knowledge of any type (notes, documents and other sources) and answers citing where each answer comes from. It runs on the user's Mac (Apple M2 Max, 64 GB), keeps data on the machine unless the user decides otherwise, and is built in small vertical slices with production-level practices from day one.

## Status

Phase 0 is in progress: the full development environment, with every piece of the architecture in its minimal working version and no real functionality.

## Documentation

- Design (in Spanish, to be translated): [docs/00-indice.md](docs/00-indice.md).
- Standards (current tools and practices): [docs/standards/](docs/standards/README.md).

## License

AGPL-3.0-or-later. The full text is in [LICENSE](LICENSE).

## Setup

Development happens only in the dev container ([ADR 0002](docs/decisions/adr/0002-dev-container.md)):

1. Install Docker Desktop and VS Code with the Dev Containers extension.
2. Clone the repository, open the folder in VS Code and choose "Reopen in Container". The first build installs the tools and dependencies (`.devcontainer/post-create.sh`, uses the network).
3. In the container's terminal, run every local check: `just check`.

Run git and the project's tools only inside the container, never on the host. See [docs/standards/repository.md](docs/standards/repository.md#dev-container) for details.

## Install a release

Only tagged releases are installed for use. Download the wheel and its provenance bundle from a [release](https://github.com/rlopc/episteme/releases), verify it, and install it with [uv](https://docs.astral.sh/uv/):

```sh
gh release download vX.Y.Z --repo rlopc/episteme --pattern '*.whl*'
gh attestation verify episteme-X.Y.Z-py3-none-any.whl --repo rlopc/episteme \
  --signer-workflow rlopc/episteme/.github/workflows/release.yml
uv tool install ./episteme-X.Y.Z-py3-none-any.whl
```

Details: [docs/standards/release.md](docs/standards/release.md).

## Contributing and security

See [CONTRIBUTING.md](CONTRIBUTING.md) and [SECURITY.md](SECURITY.md).

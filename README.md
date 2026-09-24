# Fluzo Documentation

Specifications, architecture and delivery planning for **Fluzo**, a local-first
agentic development runtime written in Rust.

**Status:** the MVP scope and architecture decisions are approved. Runtime
implementation, security verification and performance measurements are pending.
The documentation describes requirements, not features already delivered.

- [Documentation site](https://fluzo-labs.github.io/fluzo-docs/)
- [Product requirements](PRD.md)
- [Architecture and accepted decisions](ARCHITECTURE.md)
- [Organization and seed backlog](GITHUB_ORGANIZATION.md)
- [Published repositories, issue mapping and remaining access](PUBLICATION.md)
- [Implementation repository](https://github.com/fluzo-labs/fluzo)
- [Documentation issues](https://github.com/fluzo-labs/fluzo-docs/issues)

The root documents are canonical. The mdBook chapters include them directly;
edit the originals rather than duplicating their contents in `src/`.

## Build and Check

Requirements: Python 3.11+, Cargo and a Rust toolchain supported by the pinned
documentation tools. CI uses Rust 1.90.0.

```sh
cargo install mdbook --version 0.4.52 --locked
cargo install mdbook-mermaid --version 0.15.0 --locked
python3 scripts/check_docs.py
mdbook-mermaid install .
mdbook build
python3 scripts/check_docs.py --book book
```

The Mermaid command prepares ignored local assets; it does not create another
source of truth. Generated HTML goes into `book/`. No model server, GPU, Docker
or inference credentials are needed. Initial tool downloads require network
access. The workflow publishes checked `main` builds to GitHub Pages; pull
requests only validate and build.

See [CONTRIBUTING.md](CONTRIBUTING.md), [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)
and [SECURITY.md](SECURITY.md). Original project content is licensed under
[MIT](LICENSE); third-party build tools and bundled assets retain their licenses.
# Fluzo

Fluzo is a planned local-first agentic development runtime in Rust, with a
terminal interface and an independently usable execution engine.

## Current Status

The MVP product scope and architecture decisions A01-A10 are approved.
Implementation has not started: there is no released binary, tested sandbox,
completed security validation or measured performance result yet.

The initial target is Linux x86_64 on Arch Linux and CachyOS, with Ghostty and
Alacritty as reference terminals. The runtime is designed as four crates in a
single implementation repository. Documentation and required tests must not
depend on access to a private inference service.

## Design Baselines

- [Product requirements](PRD.md): approved MVP scope, future capabilities and acceptance criteria.
- [Architecture](ARCHITECTURE.md): component boundaries, accepted decisions and verification contracts.
- [Organization and backlog](GITHUB_ORGANIZATION.md): ownership and the issue seed plan.

## Repositories

- [fluzo-labs/fluzo](https://github.com/fluzo-labs/fluzo): future implementation, tests and packaging.
- [fluzo-labs/fluzo-docs](https://github.com/fluzo-labs/fluzo-docs): canonical specifications and this site.
- [Implementation issues](https://github.com/fluzo-labs/fluzo/issues)
- [Documentation issues](https://github.com/fluzo-labs/fluzo-docs/issues)

Examples in the specifications are design contracts, not installation
instructions for an existing application. Original content is MIT licensed,
copyright 2026 Jose Corral.
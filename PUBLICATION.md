# GitHub Publication Record

**Date:** 2026-09-24

**Organization:** [fluzo-labs](https://github.com/fluzo-labs)

**Administrator:** [jmanuelcorral](https://github.com/jmanuelcorral)

This record identifies provisioned resources. GitHub issues and workflow runs,
not this document, own current delivery status. There is no implemented or
released Fluzo runtime yet.

## Published Resources

| Resource | URL / evidence |
| -------- | -------------- |
| Implementation repository | [fluzo](https://github.com/fluzo-labs/fluzo) |
| Canonical specifications and site source | [fluzo-docs](https://github.com/fluzo-labs/fluzo-docs) |
| Documentation site | [fluzo-labs.github.io/fluzo-docs](https://fluzo-labs.github.io/fluzo-docs/) |
| Organization Project | [Fluzo Delivery](https://github.com/orgs/fluzo-labs/projects/1) |
| Initial documentation baseline | [60c5b0732fb710cdf705476cee8d9156a5ecd971](https://github.com/fluzo-labs/fluzo-docs/commit/60c5b0732fb710cdf705476cee8d9156a5ecd971) |
| Implementation metadata baseline | [d31a16472abc998898a6b90cc9af942340894119](https://github.com/fluzo-labs/fluzo/commit/d31a16472abc998898a6b90cc9af942340894119) |
| Initial documentation CI and Pages | [Successful workflow](https://github.com/fluzo-labs/fluzo-docs/actions/runs/36001597633) |
| Initial implementation metadata check | [Successful workflow](https://github.com/fluzo-labs/fluzo/actions/runs/36001606055) |

Both repositories are public, have MIT notices for Jose Corral, community
documents, issue/PR templates, a named code owner and private vulnerability
reporting enabled. The implementation workflow validates bootstrap metadata only;
it does not claim Rust/runtime validation. Documentation builds use mdBook
0.4.52 and mdbook-mermaid 0.15.0, with workflows pinned to action commits.

HTTP checks confirmed the index, PRD, architecture and organization pages were
served successfully. Browser inspection confirmed four rendered Mermaid diagrams
and no Mermaid error markers. Local checks parsed examples and validated the
dependency graph. These are publication checks, not acceptance of the MVP.

## Issue Mapping

There are 28 implementation issues and 5 documentation/governance issues. All
carry seed IDs, baseline links, acceptance briefs, type/area labels and the
repository's `MVP` milestone. Their 60 dependencies are linked in the bodies and
as GitHub-native blocked-by relationships. Consult the live issues for state.

| Seed ID | Issue |
| ------- | ----- |
| ORG-01 | [fluzo-docs#1](https://github.com/fluzo-labs/fluzo-docs/issues/1) |
| ORG-02 | [fluzo-docs#2](https://github.com/fluzo-labs/fluzo-docs/issues/2) |
| DOC-01 | [fluzo-docs#3](https://github.com/fluzo-labs/fluzo-docs/issues/3) |
| DOC-02 | [fluzo-docs#4](https://github.com/fluzo-labs/fluzo-docs/issues/4) |
| FND-01 | [fluzo#1](https://github.com/fluzo-labs/fluzo/issues/1) |
| FND-02 | [fluzo#2](https://github.com/fluzo-labs/fluzo/issues/2) |
| FND-03 | [fluzo#3](https://github.com/fluzo-labs/fluzo/issues/3) |
| FND-04 | [fluzo#4](https://github.com/fluzo-labs/fluzo/issues/4) |
| SIM-01 | [fluzo#5](https://github.com/fluzo-labs/fluzo/issues/5) |
| UI-01 | [fluzo#6](https://github.com/fluzo-labs/fluzo/issues/6) |
| UI-02 | [fluzo#7](https://github.com/fluzo-labs/fluzo/issues/7) |
| UI-03 | [fluzo#8](https://github.com/fluzo-labs/fluzo/issues/8) |
| UI-04 | [fluzo#9](https://github.com/fluzo-labs/fluzo/issues/9) |
| UI-05 | [fluzo#10](https://github.com/fluzo-labs/fluzo/issues/10) |
| DAT-01 | [fluzo#11](https://github.com/fluzo-labs/fluzo/issues/11) |
| DAT-02 | [fluzo#12](https://github.com/fluzo-labs/fluzo/issues/12) |
| OBS-01 | [fluzo#13](https://github.com/fluzo-labs/fluzo/issues/13) |
| OBS-02 | [fluzo#14](https://github.com/fluzo-labs/fluzo/issues/14) |
| RUN-01 | [fluzo#15](https://github.com/fluzo-labs/fluzo/issues/15) |
| RUN-02 | [fluzo#16](https://github.com/fluzo-labs/fluzo/issues/16) |
| RUN-03 | [fluzo#17](https://github.com/fluzo-labs/fluzo/issues/17) |
| RUN-04 | [fluzo#18](https://github.com/fluzo-labs/fluzo/issues/18) |
| RUN-05 | [fluzo#19](https://github.com/fluzo-labs/fluzo/issues/19) |
| AGT-01 | [fluzo#20](https://github.com/fluzo-labs/fluzo/issues/20) |
| AGT-02 | [fluzo#21](https://github.com/fluzo-labs/fluzo/issues/21) |
| AGT-03 | [fluzo#22](https://github.com/fluzo-labs/fluzo/issues/22) |
| AGT-04 | [fluzo#23](https://github.com/fluzo-labs/fluzo/issues/23) |
| REL-01 | [fluzo#24](https://github.com/fluzo-labs/fluzo/issues/24) |
| REL-02 | [fluzo#25](https://github.com/fluzo-labs/fluzo/issues/25) |
| REL-03 | [fluzo#26](https://github.com/fluzo-labs/fluzo/issues/26) |
| REL-04 | [fluzo#27](https://github.com/fluzo-labs/fluzo/issues/27) |
| DOC-03 | [fluzo-docs#5](https://github.com/fluzo-labs/fluzo-docs/issues/5) |
| REL-05 | [fluzo#28](https://github.com/fluzo-labs/fluzo/issues/28) |

## Import Tool

The script in `scripts/sync_backlog.py` is dry-run by default. It detects existing
seed IDs rather than overwriting issue bodies or creating duplicates. An explicit
apply invocation requires a published immutable documentation baseline. Native
dependency creation is separately selected and never removes existing edges.

```sh
python3 scripts/sync_backlog.py
python3 scripts/sync_backlog.py --apply --link-dependencies \
  --baseline 60c5b0732fb710cdf705476cee8d9156a5ecd971 \
  --report .tools/backlog-import.json
```

No token is written to a report or repository. The script invokes the already
authenticated GitHub CLI; it does not request credentials itself.

## Fluzo Delivery Project

The account owner completed Project authorization directly with GitHub on
2026-09-24. The public organization-level
[Fluzo Delivery](https://github.com/orgs/fluzo-labs/projects/1) Project now links
both repositories and contains all 33 existing issues, without duplicating or
rewriting them. Native dependencies remain the same 60 relationships.

Six fields are configured: Status, Priority, Delivery, Area, Size and Blocked.
Status has Backlog, Ready, In progress, In review and Done. Priority, Delivery
and Area reflect the seed plan. Initial Status reflects known completion or
active work; Blocked reflects open prerequisites. Size and assignees remain
unset rather than inventing estimates or allocating people.

| View | Purpose |
| ---- | ------- |
| [All issues](https://github.com/orgs/fluzo-labs/projects/1/views/1) | Table of the complete linked backlog |
| [MVP board](https://github.com/orgs/fluzo-labs/projects/1/views/2) | Status columns, excluding Post-MVP work |
| [Ready](https://github.com/orgs/fluzo-labs/projects/1/views/3) | Open Ready work with no recorded blocker, ordered by priority/delivery |
| [Blocked](https://github.com/orgs/fluzo-labs/projects/1/views/4) | Open blocked issues grouped by delivery stage |
| [TUI and design](https://github.com/orgs/fluzo-labs/projects/1/views/5) | TUI and configuration work grouped by status |
| [Runtime and security](https://github.com/orgs/fluzo-labs/projects/1/views/6) | Core, runtime, security, provider and storage work grouped by area |
| [Documentation](https://github.com/orgs/fluzo-labs/projects/1/views/7) | Issues owned by fluzo-docs, grouped by status |
| [Post-MVP](https://github.com/orgs/fluzo-labs/projects/1/views/8) | Explicitly deferred work; initially empty |

These are views of the same issues, not separate boards to synchronize. Blocked
and Ready need maintainer triage when dependency states change; no automatic
scheduling or continuous dependency-field refresh is implied. Project creation
does not start implementation or authorize a release. Governance evidence and
the reviewed publication update are tracked by
[ORG-02](https://github.com/fluzo-labs/fluzo-docs/issues/2).
# Fluzo GitHub Organization and Backlog

**Status:** Provisioning authorized; publication in progress
**Version:** 0.2
**Date:** 2026-09-24
**Product owner:** Jose Corral
**Baseline:** [PRD.md](PRD.md) v0.2 and [ARCHITECTURE.md](ARCHITECTURE.md) v0.1, decisions A01-A10 accepted
**Language:** English for repository documentation, issues, pull requests and project fields

## 1. Recommendation and Scope

Create a GitHub organization with two initial repositories: `fluzo` for the implementation and `fluzo-docs` for product specifications, architecture and the documentation site. Use one organization-level GitHub Project to view work from both. Keep core, runtime, TUI and CLI together in one Cargo workspace inside `fluzo`.

A crate is a compilation/dependency boundary; a repository is a source-control, contribution and release boundary. Accepted A01/A02 require separable components, not separate repositories. A runtime/TUI change should normally be implementable, reviewed and tested in one pull request. Avoid independent versioning, cross-repository dependency pins and coordinated release trains until there is an actual need.

This document defines repository governance and the initial backlog, not new product features. On 2026-09-24, Jose Corral authorized the public `fluzo-labs/fluzo` and `fluzo-labs/fluzo-docs` repositories, documentation publication through mdBook/GitHub Pages, and issue/Project provisioning. The user created the organization; authenticated membership for `jmanuelcorral` was verified as active administrator. Publication results and actual resource links will be recorded separately from this plan. This authorization does not approve an application release or implementation work beyond repository/documentation setup.

## 2. Organization and Repository Map

The selected and created organization is [fluzo-labs](https://github.com/fluzo-labs), administered by [jmanuelcorral](https://github.com/jmanuelcorral). Both initial repositories, their backlog and the documentation site are authorized for public visibility. This is not a trademark-clearance claim. The public product name remains Fluzo and the executable remains `fluzo`; actual feature/plan permissions must still be checked during provisioning.

| Repository | Initial responsibility | Explicit exclusions |
| ---------- | ---------------------- | ------------------- |
| `fluzo` | The four-crate Cargo workspace, native binary, tests/fixtures, HTTP simulators, local observability Compose/configuration, CI, packaging and release artifacts | No separate production services for each module; no model weights, private endpoints, credentials or user history |
| `fluzo-docs` | Authoritative product/architecture specifications, design decisions, roadmap, guides, documentation-site source and its deployment | No duplicate implementation, task database, independent runtime config schema or copies of application tests |

An optional organization `.github` repository can later host the organization profile and genuinely shared community templates. It is not needed to build the MVP and must not become a third place for product requirements, implementation work or a copied backlog.

Do not initially create repositories for `fluzo-core`, `fluzo-runtime`, `fluzo-tui`, `fluzo-cli`, Laya, observability, plugins, memory, or packaging. Keep these as crates, modules, test support or directories in the owning repository as applicable. The existing local directory name `fluxcon` does not require a GitHub repository with the same name.

### 2.1 Implementation Repository

Proposed layout, to materialize incrementally rather than create empty directories:

```text
fluzo/
  Cargo.toml
  Cargo.lock
  crates/
    fluzo-core/
    fluzo-runtime/
    fluzo-tui/
    fluzo-cli/
  tests/
    fixtures/
    support/
  observability/
  packaging/arch/
  docs/development/
  .github/workflows/
```

Compose and its backend configuration live with the runtime instrumentation and integration tests they validate. The PKGBUILD lives with its binary and release workflow. Rust API documentation stays with the code and is generated from doc comments; developer commands and local setup instructions change atomically with the implementation.

### 2.2 Documentation Repository

Use Markdown and mdBook with GitHub Pages for the first site, as authorized by the user. Tool versions must be pinned and the build checked before publication. No custom domain is configured initially. The repository-root specifications remain canonical; thin mdBook include chapters render them without maintaining duplicate document bodies.

Proposed source layout:

```text
fluzo-docs/
  PRD.md
  ARCHITECTURE.md
  GITHUB_ORGANIZATION.md
  book.toml
  src/
    SUMMARY.md
    index.md
    PRD.md                  # includes the canonical root document
    ARCHITECTURE.md         # includes the canonical root document
    GITHUB_ORGANIZATION.md  # includes the canonical root document
  .github/workflows/
```

Specifications and future proposals must be clearly distinguished from documentation of implemented/released behavior. Publishing the approved PRD does not make the product usable. The initial site can expose specifications and implementation status; installation/tutorial pages must not advertise nonexistent commands as runnable.

## 3. Sources of Truth and Cross-Repository Changes

Until migration occurs, the local [PRD.md](PRD.md) and [ARCHITECTURE.md](ARCHITECTURE.md) remain authoritative. After an explicitly approved transfer, the corresponding documents in `fluzo-docs` become canonical. Preserve their revision history, decision dates and references where practical. Update relative links and remove obsolete full copies from the implementation repository only as part of that reviewed migration; leave discoverable links to the new canonical documents.

| Information | Canonical owner | Link from the other repository |
| ----------- | --------------- | ------------------------------ |
| Product scope and architecture baseline | `fluzo-docs` | Code README/contribution guide and work-item references |
| Actual behavior, config types/defaults and API docs | `fluzo` | Guides reference implementation/release revisions; no second hand-maintained schema |
| Build/test/release commands and developer setup | `fluzo` | Site links to the tested instructions for the matching revision |
| User guides and product roadmap | `fluzo-docs` | Code README links to current/released documentation |
| Tasks, bugs and delivery status | Issues in the owning repository | Organization Project aggregates them; no duplicated Markdown status board |
| CI results and release evidence | Owning workflow/run and release | Issues/docs link to immutable runs/artifacts and their revision |

An implementation milestone records the exact documentation commit used as its baseline, not just a moving link to `main`. A specification revision and an application release number are different version spaces. Public guides identify which release or unreleased development state they describe; the site does not silently reinterpret an older release using new defaults.

A scope/security/defaults change starts with an explicit specification/design review in `fluzo-docs`, linked to any implementation issue/PR in `fluzo`. Merge the approved design first or record an explicit dependency; do not require mutually blocking PRs. Pure implementation corrections inside the approved contract do not need a new PRD version. Behavior-facing changes include a guide follow-up or linked documentation PR before release. Use commit/tag links when recording acceptance evidence.

Keep this organization plan in `fluzo-docs` after migration. The seeded backlog below is an import proposal: once issues exist, their status, assignees and dependencies are authoritative. Do not maintain two conflicting progress trackers.

## 4. Organization-Level Project

Create one GitHub Project owned by the organization, provisionally named **Fluzo Delivery**. Projects provide views over repository issues; they are not another repository or the canonical task database. Public contributors should be able to find the owning issues even if the chosen Project visibility is restricted.

Use these initial fields without duplicating information already supplied by GitHub:

| Field | Values / purpose |
| ----- | ---------------- |
| Status | Backlog, Ready, In progress, In review, Done |
| Priority | P0: blocker/critical risk; P1: planned MVP delivery; P2: explicitly deferred work |
| Delivery | M0 Setup, M1 Foundation, M2 Visual prototype, M3 Diagnostics/storage, M4 Safe execution, M5 Native agent, M6 Release, Post-MVP |
| Area | Core, Runtime, TUI, Config, Storage, Security, Providers, Observability, Tests, Packaging, Docs, Governance |
| Size | S, M, L; split L delivery work before moving it to Ready rather than treating it as a precise time estimate |
| Blocked | Yes/No plus a linked blocker and explanation in the issue; never use the flag alone |

Use built-in repository, labels, assignees and linked-PR information rather than manually copied text fields. Keep the field set small. Add iterations or dates only when there is an actual delivery cadence, not speculative deadlines for an unimplemented MVP.

Recommended views are: MVP board grouped by status; Ready ordered by priority/dependency; blocked work; TUI/design review; runtime/security; documentation; and Post-MVP. Filters distinguish a prototype demonstration from completed runtime behavior. A successful demo is not a release-ready task engine.

GitHub repository milestones are repository-scoped. Use the Project's Delivery field for the shared cross-repository milestones, and reserve repository milestones for concrete release tracking where useful. Application tags, PRD versions and architecture document versions must not be inferred from each other.

### 4.1 Issues, Epics and Pull Requests

Repository issues own deliverables. An epic is an umbrella issue containing child issues or an explicit checklist of links, not a second copy of the same acceptance criteria. Use native parent/dependency relationships when available; a `Depends on` section with qualified issue links is sufficient otherwise. Do not depend on a paid feature merely to track blockers.

File application behavior, testing and packaging work in `fluzo`. File specification, guide/site and governance work in `fluzo-docs`. A bug reported in the wrong repository is triaged/transferred or linked to its owner, not silently duplicated. Use Discussions for open-ended product/design discussion if enabled; a decision affecting delivery must be summarized in a linked issue or design PR.

Adopt a small label vocabulary: `type:feature`, `type:bug`, `type:design`, `type:spike`, `type:docs`, `type:chore`, plus a limited `area:*` set matching the ownership boundaries. Keep priority/status in Project fields, not conflicting labels. `good first issue` and `help wanted` are added only when a maintainer has scoped the work sufficiently.

Each ready issue contains:

```text
Goal / user or engineering outcome
Owning repository and area
PRD sections, architecture decision IDs and baseline revision
In scope / explicitly out of scope
Acceptance criteria with observable results
Verification profile and evidence to attach
Dependencies and linked design decisions
Security, privacy and performance risks where applicable
Documentation impact
```

Ready means the outcome and test strategy are clear, required design decisions are resolved, dependencies permit starting, and the issue fits a reviewable increment. Done means the implementation or document is merged, applicable checks/evidence are attached, and documentation is current. A spike is Done when it reports its experiment, limitations and a recorded decision, not when it quietly adds production behavior. A blocked or skipped required validation is not a pass.

Use short-lived branches and small PRs into `main`. Link every implementation PR to the owning issue and its design references. Use automatic issue-closing keywords only when all of that issue's acceptance criteria are satisfied; completing one child must not close an epic. Cross-repository changes link to one another explicitly, with an order of integration and no circular merge dependency.

Limit active work initially to one implementation slice plus, if useful, one independent documentation/review task. The Project is for actual status, not a reason to start every milestone at once. No particular person or agent is automatically assigned by this draft.

## 5. Governance, Permissions and Automation

### 5.1 Ownership and Review

Jose Corral is the initial product owner and proposed organization owner, subject to confirming the GitHub account. Do not infer the account handle from a local username. Require strong account authentication and keep recovery credentials outside repositories/issues. Add another trusted recovery owner when one is available; do not create fictitious teams or grant owner access to automation merely for convenience.

Use least-privilege repository roles and default member access. Teams such as Maintainers or Docs are optional when there are actual collaborators, not required scaffolding. `CODEOWNERS` should identify real maintainers for configuration, runtime/security, release workflows and documentation as staffing permits. Code ownership aids review; it is not an authorization boundary for agent execution.

Protect `main` against deletion and force pushes and require PRs and the applicable CI checks once those checks actually exist. In a single-maintainer project, do not require a different-person approval that makes every PR impossible to merge; retain a recorded self-review and CI evidence. Once a second reviewer is available, require one peer approval and relevant owner review for sensitive paths. Any emergency bypass is explicit and documented, not the normal workflow. Confirm ruleset/environment features against the selected GitHub plan before claiming them as enforced.

Provide contribution instructions, a code of conduct, PR/issue templates, a security-reporting route, and MIT license text with `Copyright (c) 2026 Jose Corral`. Project-authored docs use the same license unless separately agreed; third-party screenshots, artwork and dependencies keep their licenses. Security disclosures and secrets do not belong in public issues. If private vulnerability reporting is unavailable, document a reviewed contact route before public launch.

### 5.2 CI and Release Boundaries

| Workflow class | Owner | Required behavior |
| -------------- | ----- | ----------------- |
| Rust PR checks | `fluzo` | Formatting/lint/build, domain/protocol/config tests, dependency-boundary checks and applicable deterministic E2E; no real inference |
| TUI validation | `fluzo` | Buffer/PTY scenarios in CI; recorded Ghostty/Alacritty design/performance review on documented reference environments |
| Observability integration | `fluzo` | Dedicated Docker-capable job with simulators and real local telemetry backends; no model credentials or GPU |
| Package/release candidate | `fluzo` | Locked dependencies, archives/checksums and PKGBUILD checks, with Arch/CachyOS evidence; inference-independent |
| Documentation PR checks | `fluzo-docs` | Markdown/site build, local links, example syntax and internal references; distinguish planned from implemented features |
| Pages deployment | `fluzo-docs` | Deploy a checked artifact from trusted `main` or an explicitly selected documentation revision, not arbitrary fork code |
| Live-model evaluation | Explicitly authorized operator/profile | Optional; finite budgets, authorized targets and separate results; never a mandatory PR, fork or release condition |

Ordinary test runs use isolated configuration and fixture-only network destinations. Dependency/image downloads are prepared separately; this is not a promise of offline bootstrapping. Do not run untrusted fork code on a personal workstation, inference server or a runner carrying deployment credentials. Keep any hardware-specific/manual validation separate from untrusted PR execution.

Default workflow token permissions are read-only. Give deployment/release jobs only the permissions they need; Pages may require scoped Pages/OIDC permissions without a broadly privileged personal token. Pin actions and dependency/tool versions appropriately and update them through reviewed PRs. Never use a privileged PR workflow to check out and execute untrusted changes with secrets. Provider credentials are not an organization-wide secret required for building Fluzo.

As checks are introduced, add stable named required gates for completed slices. Do not claim unimplemented test layers are passing by installing empty workflows. Code-generation artifacts and documentation builds record source revisions; generated files do not become an alternative editable source of truth.

Release artifacts belong to `fluzo`; the documentation site belongs to `fluzo-docs`. Publishing or creating tags is an explicit maintainer action/workflow, not an automatic consequence of approving this organization plan. AUR publishing is post-MVP even though the source PKGBUILD is a required deliverable. Do not commit model weights, recorded private conversations, `.fluzodrive/`, real credentials, or machine-specific `.fluzo` settings into either repository.

## 6. Seed Backlog

The following are proposed issue briefs, not existing GitHub issues. IDs such as `FND-01` are local planning references and must be mapped to real qualified issue links during import. Every row starts in Backlog with no assignee. Dependencies mean prerequisite accepted behavior, not permission to bypass a safety gate. Milestones are exit checkpoints; an independent test/support issue may start earlier when its listed dependencies are satisfied.

These entries seed the backlog rather than replace PRD section 53. Before marking a delivery issue Ready, split it if necessary and expand its acceptance criteria using the linked specification sections. Before calling the backlog complete, map every MVP acceptance requirement to an owning issue and evidence; omit no requirement just because it is not a row below.

### 6.1 M0: Organization and Documentation Setup

| ID | Repository | Priority | Deliverable | Depends on | Acceptance brief |
| -- | ---------- | -------- | ----------- | ---------- | ---------------- |
| ORG-01 | `fluzo-docs` | P0 | Confirm identity and provision organization/repositories | - | Confirm handle/account/visibility/plan and explicitly authorize provisioning; create only the two agreed repositories. This bootstrap checklist can be recorded as an issue after the docs repository exists. |
| ORG-02 | `fluzo-docs` | P1 | Project, issue conventions and repository governance | ORG-01 | One organization Project aggregates both repositories; labels/fields/templates and feasible solo-maintainer rules are documented and exercised with a sample issue/PR. |
| DOC-01 | `fluzo-docs` | P0 | Transfer canonical specifications and record baseline | ORG-01 | PRD, architecture and this plan have one canonical location; preserve history where practical, fix links and record immutable baseline references without losing local changes. |
| DOC-02 | `fluzo-docs` | P1 | Documentation site build and publication pipeline | DOC-01 | A pinned mdBook build and link/example checks pass; Pages deployment is explicitly authorized, with approved visibility and clear planned-versus-released status. |

### 6.2 M1: Foundation

| ID | Repository | Priority | Deliverable | Depends on | Acceptance brief |
| -- | ---------- | -------- | ----------- | ---------- | ---------------- |
| FND-01 | `fluzo` | P0 | Four-crate Cargo workspace and build baseline | ORG-01, DOC-01 | Binary/library boundaries match A01, MIT metadata and lockfile are present, toolchain/MSRV choice is recorded, and core/TUI/runtime have no forbidden dependency edges. |
| FND-02 | `fluzo` | P0 | Typed settings registry and canonical defaults | FND-01 | File/default/UI descriptors agree, validation covers cross-field constraints, unknown fields fail clearly, and secret references remain distinct from values (A06). |
| FND-03 | `fluzo` | P0 | Application port, domain states and scenario driver | FND-01 | Commands, snapshots, versions and structured errors support pure fixtures; inspection cannot execute work and the TUI has no direct runtime dependency (A02/A07). |
| FND-04 | `fluzo` | P1 | Initial inference-independent PR checks | FND-01 | Formatting, lint/build/unit and dependency-boundary checks run from a clean checkout; fork execution needs no private config or inference secrets. |
| SIM-01 | `fluzo` | P1 | HTTP scenario test harness | FND-03 | Ephemeral loopback servers validate expected/missing requests, fragmented streams and negative responses; isolated settings and no fallback to live services (A08). |

### 6.3 M2: Visual Prototype

| ID | Repository | Priority | Deliverable | Depends on | Acceptance brief |
| -- | ---------- | -------- | ----------- | ---------- | ---------------- |
| UI-01 | `fluzo` | P0 | Terminal shell, composer and command palette | FND-03 | English demo navigation preserves drafts/focus; streaming cannot steal input, bracketed paste is safe and terminal state is restored on exit. |
| UI-02 | `fluzo` | P1 | Original logo, themes, animation and devmenu | UI-01, FND-02 | Runtime-shaped demo states drive the pixel logo; 60/30/15/0 FPS and reduced motion work; previews revert and no visual flag grants runtime authority. |
| UI-03 | `fluzo` | P1 | Welcome and typed configuration workflow | UI-01, FND-02 | Missing config opens setup; existing valid config skips it; temporary-fixture save/reload, defaults, conflicts and CLI overrides are tested without contacting models. |
| UI-04 | `fluzo` | P1 | Tasks, permissions, diff and notification demo states | UI-01 | Selecting a task does not resume it; cancel/kill controls are distinct; permission focus is safe; content is sanitized; every simulated result is visibly synthetic. |
| UI-05 | `fluzo` | P0 | First visual and interaction review | UI-02, UI-03, UI-04 | Attach PTY/snapshot evidence for specified viewports plus Ghostty/Alacritty recordings and Jose's review; log findings as issues rather than claiming runtime acceptance. |

### 6.4 M3: Diagnostics and Storage

| ID | Repository | Priority | Deliverable | Depends on | Acceptance brief |
| -- | ---------- | -------- | ----------- | ---------- | ---------------- |
| DAT-01 | `fluzo` | P0 | Repository store, writer and durable journal | FND-02, FND-03 | `.fluzodrive/` is protected/ignored, WAL/FULL/foreign keys are verified, state/events commit together and crash fixtures expose unknown outcomes (A03). |
| DAT-02 | `fluzo` | P1 | Artifacts, retention, quotas, migration and purge | DAT-01 | Bounded capture, no silent expiry, recoverable backups, dry-run/confirmation, shared references and partial deletion failures are tested per repository. Split into focused child issues before implementation. |
| OBS-01 | `fluzo` | P0 | Three-path diagnostics and pinned GenAI instrumentation | DAT-01, FND-03, SIM-01 | SQLite audit is separate from bounded JSONL/OTLP sinks; all signals and token accounting match A09; privacy, drops and failed-sink responsiveness are tested. |
| OBS-02 | `fluzo` | P1 | Local Compose and provisioned dashboards | OBS-01 | A synthetic run reaches all three backends with trace/log correlation; credentials, loopback exposure, restart persistence and collector-outage checks are documented. |

### 6.5 M4: Safe Execution

| ID | Repository | Priority | Deliverable | Depends on | Acceptance brief |
| -- | ---------- | -------- | ----------- | ---------- | ---------------- |
| RUN-01 | `fluzo` | P0 | Workspace identity, writer ownership and native file confinement | DAT-01, DAT-02 | Two local runtimes cannot write one workspace; path/link/race/protected-path fixtures fail closed; user changes remain protected. |
| RUN-02 | `fluzo` | P0 | Policy, grants, consent and session YOLO | RUN-01, FND-02 | Denials win, grants have exact scope/lifetime, headless approval does not hang, and repository config cannot silently authorize sensitive changes. |
| RUN-03 | `fluzo` | P0 | Native tools and owned process lifecycle | RUN-02, DAT-02 | Direct args by default, explicit shell, closed stdin, reviewed environment, safe Git inspection and bounded output; cancellation/kill never targets unrelated processes. |
| RUN-04 | `fluzo` | P0 | Session recovery and private task-control channel | RUN-03 | Open/replay is read-only; resume reconciles versions/unknown outcomes and preserves budget; inspection clients cannot start a second writer or restore YOLO. |
| RUN-05 | `fluzo` | P0 | Task budgets and per-process inference admission | DAT-01, FND-02, SIM-01 | All local request paths honor model/pool limits, queues and foreground reservations; independent processes do not coordinate server quotas; 429 never triggers automatic recovery. |

### 6.6 M5: Native Agent

| ID | Repository | Priority | Deliverable | Depends on | Acceptance brief |
| -- | ---------- | -------- | ----------- | ---------- | ---------------- |
| AGT-01 | `fluzo` | P0 | Generative provider gateway and complete streaming contract | RUN-05, RUN-02, OBS-01 | Validated tool calls are assembled before dispatch; usage-only chunks, redirects, cancellation, non-quota retries and unknown usage are handled against HTTP fixtures. |
| AGT-02 | `fluzo` | P1 | Scoped context, explicit skills and automatic compaction | AGT-01, RUN-01 | Context is bounded/provenanced; summaries preserve source links without becoming authority; failed or oversized compaction blocks safely and remains observable. |
| AGT-03 | `fluzo` | P1 | Optional replaceable Laya shadow capability | AGT-01, RUN-05 | Enable/disable and failure-pause obey consent/capacity; observations never choose executable actions; a contract substitute does not require coordinator/UI changes (A10). |
| AGT-04 | `fluzo` | P0 | Real native loop and Rust repair acceptance | AGT-02, AGT-03, RUN-04 | Real tools reproduce/fix the synthetic bug, then independent verification checks the unchanged tests and diff; permissions, audit and failed runs remain visible. |

### 6.7 M6: Integration and Release

| ID | Repository | Priority | Deliverable | Depends on | Acceptance brief |
| -- | ---------- | -------- | ----------- | ---------- | ---------------- |
| REL-01 | `fluzo` | P0 | Complete TUI/headless runtime integration | AGT-04, UI-05 | Task inspection/cancel/kill, settings save/apply, history and diagnostics use the real application port; no simulated success appears in live mode. |
| REL-02 | `fluzo` | P0 | MVP acceptance and failure matrix | REL-01, OBS-02, FND-04 | Map every PRD section 53 item to tests/manual evidence; deterministic, Compose and optional live results are separate; required gaps block acceptance. |
| REL-03 | `fluzo` | P0 | Arch/CachyOS and terminal performance evidence | REL-02 | Record environments and measurements for Ghostty/Alacritty, large histories, input/frame/startup/memory targets and stability assumptions; no fabricated display FPS or real-inference requirement. |
| REL-04 | `fluzo` | P1 | Archive, Cargo installation and source PKGBUILD | REL-01, FND-04 | Clean builds/checksums and install/upgrade/removal preserve user data on the required distro matrix; no model dependencies or AUR publication prerequisite. |
| DOC-03 | `fluzo-docs` | P1 | Tested user guides and release-candidate documentation | REL-01, REL-04, DOC-02 | Guides reference the candidate code revision and verified commands, distinguish unsandboxed shell/YOLO and storage limits, and document inference-free testing. |
| REL-05 | `fluzo` | P0 | Release evidence review and authorized publication | REL-02, REL-03, REL-04, DOC-03 | An approved manifest links source/spec revisions, binary checksums, deterministic/manual results and known limitations; publication/tagging occurs only after explicit maintainer approval. |

### 6.8 Example of an Expanded Issue

`RUN-05` illustrates the intended level of detail before a brief becomes Ready:

```text
Title: Enforce per-process model and pool admission
Repository: fluzo
References: PRD 43.1-43.3; architecture A04, sections 5.3 and 8.2
Dependencies: DAT-01, FND-02, SIM-01

Goal:
All requests from one runtime respect configured local ceilings without
blocking the UI or coordinating unrelated Fluzo instances.

Acceptance:
- Model and pool capacity are admitted atomically.
- Streaming holds capacity through completion or recorded uncertainty.
- Local foreground queues are bounded and cancellable.
- Shadow observations cannot consume foreground-reserved capacity.
- A lower limit drains existing requests without resetting consumption.
- Two processes in different workspaces retain independent ceilings.
- HTTP 429/capacity rejection emits a clear failure and sends no retry.
- Tests use the local simulator and record overlapping-request maxima.

Not included:
Cross-process server locks, rate-limit scheduling, load balancing,
automatic failover, or live-model performance benchmarks.

Evidence:
Commands, scenario versions, observed maxima, cancellation/error outcomes,
and UI responsiveness checks linked from the implementation PR.
```

## 7. Deferred Work and Repository Extraction

Keep worktrees, active Laya plan decisions, ACP/MCP, third-party extension loading, sandboxing, long-term memory, macOS and native Windows in a distinct Post-MVP view. They may have research/design issues, but are not prerequisites for the first release. Cross-instance inference coordination and provider rate-limit management are explicitly excluded by A04 and must not reappear as automatic roadmap tasks.

Extract a repository only after there is an independently useful component, an actual maintainer/consumer boundary, a stable-enough contract, and evidence that independent releases reduce rather than increase coordination. Also account for licensing/security review, release/test ownership and downstream compatibility. A trait, a Cargo crate, or an optional feature flag alone is not a reason to split source control.

Likely future cases are externally distributed extensions with separate owners, a genuinely reusable standalone library, or a separately delivered service if B is explicitly approved. Even then, runtime extraction can first mean another executable in the same repository; process separation does not imply repository separation. Laya remains a built-in replaceable adapter in the MVP, not a separate Fluzo-maintained model repository.

Organization `.github`, package-manager distribution repositories or a domain/site repository are added only when their channel actually exists. AUR maintenance does not require a second general source repository now, and a future macOS package channel does not justify creating an empty tap today.

## 8. Provisioning and Migration Sequence

1. Approve this topology, organization handle, visibility, owner account and initial documentation-site choice. Check name availability and feature/plan constraints without interpreting them as legal clearance.
2. Obtain explicit authorization to create the organization and the two repositories. Account authentication, billing, 2FA and recovery inputs remain under the user's control; never request secrets in chat.
3. Record the current local Git state and choose an import strategy before moving anything. Preserve uncommitted work; do not reset, force-push, rewrite existing history, rename the checkout or replace remotes implicitly. Authorize any history-preserving extraction separately.
4. Transfer the canonical docs with reviewed path/link changes, then establish code-repository pointers and the baseline revision record. Publish no private model URLs, credentials or local telemetry in the process.
5. Add feasible repository protections and contribution/security policies. Register required CI checks only once their workflows can actually execute. Create the organization Project and the minimal label/field conventions.
6. Import the seed issues and record a mapping from provisional IDs to real issue URLs. Create prerequisites first or resolve all references after import. Add project membership and dependency links without inventing issue numbers or mass-assigning work.
7. Build and validate the docs site before an authorized Pages deployment; verify its public/private behavior. Leave implementation features clearly marked as planned.
8. Start the first executable slice from M1/M2 and review the prototype with simulated data. Expand the next set of issue briefs only when their design and dependencies are understood.

Provisioning is idempotent in intent: inspect existing resources before creating/updating them and report conflicts rather than deleting an organization/repository/Project. Imports should detect an existing issue by its seed ID instead of creating duplicates. Nothing in this document authorizes those API mutations yet.

## 9. Decisions to Confirm

| Decision | Proposed default | Status |
| -------- | ---------------- | ------ |
| Organization handle | `fluzo-labs` | Created by the user; administrator access verified |
| Initial repositories | `fluzo` and `fluzo-docs` | Creation authorized; results tracked in the publication report |
| Visibility | Public repositories, backlog and documentation | Explicitly approved by the user |
| Organization owner | Jose Corral, GitHub `jmanuelcorral` | Active administrator verified |
| Docs engine / publication | mdBook and GitHub Pages | Approved; deployment still requires validation |
| Backlog home | Organization Project with issues in their owning repository | Provisioning authorized; permissions/results to verify |
| Runtime/core/TUI split | Four crates in one implementation repository | Approved organization topology; runtime implementation remains pending |

No new PRD scope revision is needed merely to choose GitHub hosting and issue organization. If the repository plan introduces extra runtime features, mandatory cloud services or new release gates beyond the approved contracts, stop and review those changes explicitly.
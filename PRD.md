# Fluzo

> Lightweight, local-first agentic development runtime written in Rust.

**Status:** MVP scope approved; implementation pending
**Version:** 0.2
**Scope approval date:** 2026-09-24
**License:** MIT
**Copyright holder:** Jose Corral (2026)
**Language:** Rust
**Primary interface:** TUI
**Initial UI language:** English
**Reference terminals:** Ghostty and Alacritty on Linux
**MVP platform:** Linux x86_64 (Arch Linux and CachyOS)
**Planned future platforms:** macOS, Windows (native; release milestones TBD)

**Product identity:** Fluzo; executable `fluzo`; crate prefix `fluzo-`; project configuration file `.fluzo` (TOML, not a directory).

Fluzo's original code will be released under the MIT license with the notice `Copyright (c) 2026 Jose Corral`. Before distribution, the repository and packages MUST include the MIT license text with that notice, and Cargo/package metadata MUST declare `MIT`. Third-party code, artwork, dependencies, and model weights retain their own licenses and required notices; choosing MIT for Fluzo does not relicense them.

The name was selected on 2026-09-24 with awareness of existing uses, including the [FLUZO advertising measurement platform](https://fluzo.com/) and the unrelated [npm package `fluzo`](https://www.npmjs.com/package/fluzo). This decision does not establish trademark clearance, domain ownership, or package-name reservation. Publication identifiers and legal availability MUST be checked before public distribution; the local repository directory need not match the product name.

## MVP scope baseline

Version 0.2 is approved as the MVP product-scope baseline. Sections 34 and 53 define the first release and its acceptance requirements, supported by the detailed contracts throughout this document; section 52 defines the implementation milestones. Explicitly post-MVP capabilities and future research proposals are not first-release gates.

Remaining crate/API choices, reference-environment measurements, visual prototype review, and implementation details MUST be resolved within this scope. Changes to product scope, security guarantees, default behavior, or acceptance criteria require explicit product-owner review and a recorded PRD revision rather than silent expansion or relaxation. Runtime settings remain configurable as specified. Scope approval does not mean that the software is implemented, benchmark targets are validated, security guarantees are proven, or a release is accepted; all required implementation and verification gates remain outstanding.

Scope revision 0.2, approved on 2026-09-24: replace cross-process inference-pool ownership/arbitration with independent per-process concurrency limits. Allocation across Fluzo instances and other clients is the user's responsibility. Provider rate-limit management, automatic HTTP 429/capacity-rejection recovery, and inference coordination between processes or hosts are excluded from the MVP and the current roadmap. Configured local model/pool queues and limits, operation recovery, and the cross-process single-writer workspace contract remain required. The MVP retains one generative provider integration plus optional Laya; future provider support does not imply quota management, load balancing, or automatic failover.

---

# 1. Vision

Fluzo is a lightweight, local-first **agentic development runtime** for software engineers.

It provides a fast and beautiful terminal interface for interacting with AI coding agents while separating:

* user interface
* agent execution
* agent routing
* orchestration
* context management
* tool execution
* security policies
* verification
* persistence
* observability

Fluzo is not intended to be tied to a specific AI provider, coding agent, model, or orchestration framework.

The system should allow developers to combine:

* native Fluzo agents
* external agents through ACP
* tools through MCP
* local and cloud LLMs
* fast decision models such as Laya/Jev
* deterministic routing
* configurable agent harnesses
* multiple agents working concurrently

The fundamental goal is:

> **Turn Fluzo into a programmable operating system for AI-assisted software development.**

---

# 2. Problem

Current AI coding tools generally combine several responsibilities into a single application:

```text
UI
+
LLM
+
Agent
+
Tools
+
Permissions
+
Context
+
Memory
+
Orchestration
```

This creates several limitations:

1. Strong coupling to a specific agent implementation.
2. Limited control over how agents are selected.
3. Limited multi-agent orchestration.
4. Difficult customization of execution policies.
5. Poor portability between different agents.
6. Limited observability of agent decisions.
7. Difficult debugging of complex agent workflows.
8. Difficulty running agents in different execution environments.
9. Model cost and latency are often poorly controlled.
10. The UI becomes tightly coupled to the agent runtime.

Fluzo should instead provide a modular runtime:

```text
                       Fluzo
                          │
          ┌───────────────┼────────────────┐
          │               │                │
        Router          Harness          Context
          │               │                │
          └───────────────┼────────────────┘
                          │
                    Agent Runtime
                          │
              ┌───────────┼───────────┐
              │           │           │
           Native        ACP         ACP
            Agent        Agent       Agent
              │           │           │
              └───────────┼───────────┘
                          │
                       MCP Tools
```

---

# 3. Goals

These goals describe the overall product direction, not a requirement to ship every capability in the first release. Sections 34 and 53 define MVP scope and acceptance. Active routing, multi-agent orchestration, ACP/MCP, and remote execution remain later milestones unless explicitly identified as MVP work.

## 3.1 Primary goals

Fluzo MUST:

* provide a lightweight Rust TUI
* support interactive coding sessions
* support multiple AI agents
* support configurable agent routing
* support configurable execution harnesses
* support MCP tools
* support ACP-compatible agents
* support local and cloud models
* support persistent sessions
* support multi-agent task graphs
* support configurable permissions
* support automated verification
* provide structured event logging
* provide replay/debugging capabilities
* remain usable entirely from the terminal

---

## 3.2 Secondary goals

Fluzo SHOULD:

* support local decision models
* support Laya/Jev as routing engines
* support deterministic routing
* support dynamic agent teams
* support parallel agent execution
* support execution backends other than the local machine
* support Docker/Podman
* support remote execution
* eventually support Proxmox/Kubernetes execution
* expose a CLI API
* expose a runtime API for future UIs
* support plugins/extensions

---

# 4. Non-goals

The initial project will NOT attempt to:

* build a new foundation model
* replace every existing coding agent
* implement every possible MCP server
* implement every possible ACP agent
* build a web UI
* build an IDE
* implement distributed orchestration in the MVP
* provide a hosted SaaS platform
* automatically execute destructive operations without policy approval
* coordinate inference capacity across Fluzo instances, other clients, or hosts
* manage external provider quotas/rate limits, automatic HTTP 429 recovery, or provider failover (also absent from the current roadmap)

---

# 5. Design principles

## 5.1 Local-first

The application should work without requiring a hosted Fluzo service.

```text
Developer machine
       │
       ├── Fluzo
       ├── models
       ├── tools
       └── workspace
```

Cloud services may be used by individual agents or models.

---

## 5.2 Agent agnostic

Fluzo MUST NOT assume that one specific agent is the primary implementation.

Possible agents include:

* native Fluzo agents
* ACP-compatible agents
* custom agents
* local agents
* remote agents

---

## 5.3 Model agnostic

Models should be replaceable without changing agent definitions.

Potential providers:

* OpenAI
* Anthropic
* Google
* Azure OpenAI
* GitHub Models
* Ollama
* LM Studio
* vLLM
* custom OpenAI-compatible endpoints

---

## 5.4 Protocol first

Where a standard protocol exists, Fluzo should prefer it over proprietary integrations.

Primary protocols:

* MCP for tools/context
* ACP for external agents

---

## 5.5 Policy over hardcoding

Security and execution behaviour should be controlled through policies.

MVP example, using the same schema as section 27:

```toml
[policy]
shell = "ask"
tool_network = "deny"
git_commit = "ask"
git_push = "ask"
```

---

## 5.6 Event-driven architecture

Runtime components should communicate using structured events.

This enables:

* TUI rendering
* persistence
* telemetry
* debugging
* replay
* future web UI
* future remote clients

---

# 6. High-level architecture

```text
┌──────────────────────────────────────────────────────────────┐
│                         USER                                 │
└───────────────────────────┬──────────────────────────────────┘
                            │
                            ▼
┌──────────────────────────────────────────────────────────────┐
│                           TUI                                │
│                        ratatui                               │
└───────────────────────────┬──────────────────────────────────┘
                            │
                            ▼
┌──────────────────────────────────────────────────────────────┐
│                         RUNTIME                              │
│                                                              │
│ Session Manager                                               │
│ Task Manager                                                  │
│ Agent Coordinator                                             │
│ Event Bus                                                     │
└───────┬─────────────┬──────────────┬───────────────┬─────────┘
        │             │              │               │
        ▼             ▼              ▼               ▼
     Router        Harness        Context          Policy
        │             │              │               │
        └─────────────┴──────────────┴───────────────┘
                            │
                            ▼
                     Agent Graph
                            │
             ┌──────────────┼──────────────┐
             ▼              ▼              ▼
          Native           ACP            ACP
           Agent          Agent          Agent
             │              │              │
             └──────────────┼──────────────┘
                            │
                            ▼
                         MCP
                            │
               ┌────────────┼────────────┐
               ▼            ▼            ▼
            GitHub       Filesystem     Shell
```

---

# 7. Core components

## 7.1 TUI

The TUI is the primary user interface.

Technology:

* Rust
* Ratatui
* Crossterm

The TUI MUST remain independent from the core runtime.

The runtime MUST be usable without the TUI.

---

## 7.2 Runtime

The runtime coordinates:

* sessions
* tasks
* agents
* tools
* routing
* policies
* events
* context
* persistence

The runtime should not depend on Ratatui.

---

# 8. Agent abstraction

Agents MUST implement a common interface.

Conceptually:

```rust
trait Agent {
    async fn start(&self, context: AgentContext) -> Result<AgentRun>;
    async fn send(&self, message: Message) -> Result<AgentResponse>;
    async fn cancel(&self) -> Result<()>;
}
```

The exact API is TBD.

Agent implementations may be:

```text
NativeAgent
AcpAgent
RemoteAgent
MockAgent
```

---

# 9. Router

The Router determines which agent, tool, team or action should handle the next operation.

Routing strategies:

```text
RuleBased
ModelBased
Laya
Jev
Hybrid
```

Example:

```text
User request
     │
     ▼
   Router
     │
     ├── architect
     ├── coder
     ├── tester
     ├── security
     └── researcher
```

The router should produce structured decisions rather than natural-language explanations.

Example:

```json
{
  "decision": "coder",
  "confidence": 0.93,
  "reason_code": "implementation_task"
}
```

---

# 10. Laya/Jev integration

Laya/Jev should be treated as a **decision engine**, not necessarily as the primary generative model.

Potential use cases:

* agent selection
* tool selection
* escalation
* loop detection
* task classification
* risk classification
* verification decisions
* context selection

Example:

```text
Agent execution
      │
      ▼
   Harness
      │
      ▼
   Decision
      │
      ├── continue
      ├── retry
      ├── replan
      ├── delegate
      ├── ask_user
      └── abort
```

The system should allow replacing Laya/Jev with another decision provider.

## 10.1 Initial integration: Laya in shadow mode

The MVP MUST include an optional Laya HTTP adapter in observation-only (shadow) mode. The native agent MUST remain usable when Laya is disabled, unavailable, or returns an invalid response.

Laya receives a bounded state snapshot and typed questions through `POST /v1/systemone`; it is not a Chat Completions provider. Supported question types are `choice`, `noul`, and `score`. With llama-swap, a separately configurable decision endpoint can use `/upstream/laya/v1/systemone`.

Initial observations should classify tasks and recommend a next action from a small, predefined set. Recommendations MUST NOT execute tools, change routing, grant permissions, override budgets, or declare verification successful. Policies and actual test results remain authoritative.

Shadow requests MUST have bounded timeouts and concurrency and MUST NOT be awaited by the agent's execution path. Each request MUST reference the state and decision point observed before the corresponding action, rather than using later outcomes as prediction input. Late, failed, skipped, or cancelled observations MUST be recorded explicitly.

Non-blocking observation means no dependency on a Laya answer for authorization or task progression; it is not a guarantee of zero latency impact on shared hardware. Shared-pool observations MUST obey the foreground slot reservation in section 43.3. Enabling Laya requires an operator warning that concurrent requests, model loading/swapping, VRAM pressure, and other clients can affect Halogen even when all client-side slot limits are respected. Fluzo MUST NOT infer GPU isolation or simultaneous model residency from slot counts.

The normal settings screen and devmenu MUST expose the same `decision.enabled` control with configured/effective state, pool, available shadow allowance, and pause/skip reason. Applying or saving this control follows section 26.2 and existing destination-consent rules; it MUST NOT enable active routing or increase model/pool limits. Disabling stops new observations and removes queued ones. In-flight observations are cancelled best-effort but their slots remain occupied/uncertain until reconciled. Re-enabling MUST NOT reset unresolved slots or silently lift a paused observer.

Initial observer safeguards are one observation per decision point, at most 30 dispatched observations per task, and an automatic session-local pause after 3 consecutive transport, protocol, or timeout failures. These values MUST be editable in normal settings and persisted in `.fluzo`; an automatic pause MUST NOT rewrite the configured preference. Slow shared-server behavior MUST be visible through per-model latency/queue metrics and a user-accessible pause control. Pausing Laya MUST NOT imply that its remote process has stopped or that GPU resources have been freed.

The response schema MUST be validated, and unknown answer types, invalid probabilities, and out-of-set choices MUST be rejected. Raw option probabilities, provider confidence, and `action.act_probability` are distinct fields; none is an authorization signal.

Initial probes on 2026-09-24 reached a backend identifying itself as `convaiinnovations/laya-multilingual`. Task classification worked in one example, but `noul` incorrectly interpreted explicit prohibitions on editing in English and Spanish. A two-option `choice` also failed one of those cases. These synthetic probes establish API connectivity, not decision quality or calibrated confidence.

Promotion to active routing is outside the MVP and requires domain-specific evaluation, calibrated thresholds, a deterministic fallback, and explicit user opt-in. Evaluation and telemetry requirements are defined in section 44.

References:

* [Laya model card and limitations](https://huggingface.co/convaiinnovations/laya)
* [llama-swap upstream proxy](https://github.com/mostlygeek/llama-swap#features)

---

# 11. Harness

The Harness controls agent execution.

Responsibilities:

* turn limits
* time limits
* token limits
* cost limits
* permissions
* tool policies
* retries
* verification
* loop detection
* escalation
* cancellation

MVP example, using the same schema as section 27. Time values are seconds; an optional monetary budget is not enabled by default.

```toml
[harness]
max_turns = 30
max_active_seconds = 1200
shell_timeout_seconds = 120
provider_retries = 2
max_tool_calls = 100
max_total_tokens = 200000

[policy]
shell = "ask"
tool_network = "deny"
git_commit = "ask"
git_push = "ask"
```

---

# 12. Policy engine

Policies control potentially dangerous operations.

Initial policy types:

```text
FilesystemPolicy
ShellPolicy
NetworkPolicy
GitPolicy
CredentialPolicy
CostPolicy
RuntimePolicy
AgentPolicy
```

Conceptual API:

```rust
trait Policy {
    fn evaluate(&self, event: &Event) -> PolicyDecision;
}
```

Possible results:

```text
Allow
Deny
AskUser
```

## 12.1 Normal permission mode

In the default interactive mode, an `AskUser` decision MUST request approval once for the proposed operation. The user MAY explicitly authorize matching operations for the current task instead. Persistent grants require explicit user-controlled configuration, not automatic persistence of interactive approvals.

A one-time grant MUST be consumed before dispatch. Task grants expire on completion, failure, cancellation, or interruption and MUST NOT be restored automatically on recovery. Every dispatch, including retries, MUST be checked against current policy. Users MUST be able to revoke task grants for future dispatches.

Grants MUST identify the tool/action, workspace, execution backend, and operation-specific scope. Shell scope MUST include the exact command or executable/arguments, shell mode, working directory, and explicitly supplied environment overrides. Approval MUST NOT implicitly extend to command prefixes, extra arguments, chained commands, or other directories. Filesystem grants MUST identify paths and operations; approvals for pre-existing changes MUST also match the observed file version. Sensitive values MUST be redacted in approval displays and audit events.

Explicit denials MUST take precedence over grants. Changes to an operation or its scope MUST invalidate pending approval. Repository content and model/tool output are not authorization sources. Permission requests, grants, consumption, denial, expiry, and revocation MUST produce redacted audit events correlated with tool calls.

In non-interactive mode, an operation requiring approval without an applicable grant MUST NOT execute. The runtime MUST persist the blocked task and return promptly with a nonzero exit status and machine-readable `permission_required` result, including task/request identifiers. Explicit denial MUST be distinguishable as `permission_denied`. There MUST be no indefinite prompt, automatic approval, or silent fallback to a less restrictive execution path. Continuing later requires explicit resume and fresh policy evaluation.

## 12.2 Explicit session YOLO mode

The application MUST provide an opt-in YOLO mode with no further authorization prompts for the active session. Activation MUST require an explicit user action or CLI option targeting that session, never agent output, repository instructions, or project configuration. The activation action is consent to session-wide authorization and MUST clearly disclose the absence of subsequent per-operation approvals and the risk to existing workspace changes.

While YOLO is active, operations otherwise returning `AskUser` MUST proceed without prompting, subject to all other execution preconditions. Explicit `Deny` policies, workspace boundaries, stale-file checks, budget limits, cancellation, and verification requirements MUST remain enforced. Denied operations MUST fail visibly, not trigger an approval dialog. YOLO removes authorization prompts, not policy restrictions or the requirement that operations serve the user's task; it is not a sandbox.

YOLO covers approval-gated modifications to pre-existing user changes within the permitted workspace, but MUST NOT authorize blindly applying stale edits or discarding unrelated work. File-version checks and baseline tracking in section 21.1 remain mandatory. Existing constraints against automatic Git operations remain unchanged. After an interruption, uncertain side effects MUST be reconciled under section 22.1 rather than replayed automatically.

The mode MUST be continuously visible in the TUI and reported in CLI status, session metadata, and correlated policy events. Automatic authorizations MUST be attributed to YOLO rather than recorded as individual user approvals. The user MUST be able to disable YOLO for subsequent dispatches; doing so does not undo completed actions or cancel running commands. Pending operations MUST be re-evaluated before dispatch when the mode changes.

YOLO MUST affect only the selected active session, not other sessions or a global default. Exiting or recovering that session MUST deactivate it. Historical activation remains auditable, but ordinary resume MUST NOT re-enable it without a new explicit user action. Non-interactive runs MAY explicitly select YOLO; otherwise normal permission behavior applies. Requests for missing task information may still block progress, but MUST be distinguished from authorization requests.

---

# 13. Tool system

Tools should be represented by a common abstraction.

```rust
trait Tool {
    async fn execute(
        &self,
        request: ToolRequest
    ) -> Result<ToolResult>;
}
```

Native tools may include:

```text
filesystem
shell
git
search
process
```

External tools should be exposed through MCP.

---

# 14. MCP

Fluzo MUST support MCP clients.

MCP servers should be dynamically configurable.

Example:

```toml
[[mcp.server]]
name = "github"
command = "github-mcp-server"

[[mcp.server]]
name = "filesystem"
command = "..."
```

MCP should not be tightly coupled to individual agents.

The runtime should control MCP permissions through the Policy Engine.

---

# 15. ACP

Fluzo SHOULD support ACP as the standard mechanism for interacting with external coding agents.

Example:

```text
Fluzo
   │
   ▼
ACP Adapter
   │
   ├── external agent A
   ├── external agent B
   └── external agent C
```

ACP agents should appear to the orchestration layer as regular `Agent` implementations.

---

# 16. Context Engine

The Context Engine builds task-specific context.

Potential sources:

```text
workspace files
git status
git diff
git history
README
AGENTS.md
CLAUDE.md
skills
LSP
symbols
task history
agent outputs
tool outputs
```

Context should be selected based on task relevance.

For the MVP, initial context MUST be small and assembled deterministically from the user request, assigned workspace, Git status, and applicable `AGENTS.md` instructions. The agent MAY discover and read additional files through policy-controlled search/read tools; the entire repository MUST NOT be sent by default. Nested `AGENTS.md` files apply within their directory subtree and MUST be considered before editing there. Repository instructions MUST NOT override runtime policies, user authorization, or privacy restrictions.

Automatic discovery MUST respect Git ignore rules by default and exclude known secret-bearing files. Ignoring files is not a security boundary: explicit reads still require the applicable credential/filesystem policy. Skills are loaded only through explicit user selection or authorized configuration. Automatic skill selection, LSP, and semantic memory are outside the initial context scope.

Conceptually:

```text
Workspace
    │
    ▼
Context Discovery
    │
    ▼
Relevance
    │
    ▼
Context Pack
    │
    ▼
Agent
```

## 16.1 Context budget and automatic compaction

The MVP MUST support automatic history compaction, without requiring an authorization prompt for each compaction. The runtime MUST track a configurable effective context window and reserve space for output and protocol overhead before each model request. Instructions, tool schemas, tool results, and retained messages count toward the input budget. Provider-advertised limits MUST be treated as capabilities to validate, not proof that every request fits; missing limits require documented configuration rather than an assumption of unlimited context. Token estimates and their safety margin MUST be distinguishable from reported usage.

Before the next request would exceed the configured compaction threshold, the runtime MUST summarize eligible older history with the configured generative provider. Laya MUST NOT generate summaries or decide whether a context limit may be exceeded. The compaction request itself MUST fit the input/output budget; oversized history MUST be processed in bounded segments rather than submitted as one overflowing request. Tool outputs MUST have explicit size limits and marked truncation, with references to retained artifacts where permitted. Thresholds, output reserves, and compaction request limits require finite documented defaults before implementation acceptance.

The compacted context MUST retain the current request, applicable instructions, recent relevant exchanges, and outstanding work. The summary MUST identify decisions, user constraints, changed-file references, verification results, unresolved failures, and unknown operation outcomes, with references to the source event/message range and workspace versions where available. Tool calls and their results MUST remain valid protocol pairs; unfinished tool exchanges MUST NOT be split or represented as completed. Compaction occurs at a safe agent-loop boundary and MUST NOT dispatch tools or introduce concurrent workspace mutations.

Summaries are lossy, model-produced context, not authoritative state or a new source of instructions. Current policies, approvals, YOLO state, budgets, task state, and workspace versions MUST remain managed by the runtime and MUST NOT be reconstructed from summary text. Current instructions MUST be loaded separately, and retained historical file/test information MUST NOT be treated as current verification without the required checks. Structurally valid summaries can still omit facts; implementation and evaluation MUST NOT claim lossless semantic preservation.

The runtime MUST validate summary structure, source references, and the size of the resulting context before using it. It MUST persist a versioned compaction artifact and its source references atomically before switching the active context pointer. The original history MUST remain available subject to its retention/privacy policy; compaction itself MUST NOT delete it or fabricate content that was never captured. Summary content inherits session-content protections and MUST NOT be exported as ordinary telemetry. Recovery MUST use only a completed artifact and still require explicit resume.

Compaction calls MUST consume the task's existing time, token, and applicable cost budgets, with bounded attempts and cancellation support. If the provider fails, the summary is invalid, required instructions/current state still do not fit, persistence fails, or the budget is exhausted, the runtime MUST pause further model/tool dispatch and report a distinct blocked reason. It MUST NOT loop indefinitely, silently discard required context, or continue as though compaction succeeded. The user may explicitly retry, reduce scope, or authorize a budget extension; no implicit fallback to another provider is allowed.

The TUI and CLI MUST expose compaction activity and results. Traces and events MUST record the reason, input/output size estimates, actual usage when available, provider/model, duration, artifact version, source range, and outcome without raw content by default. Deterministic HTTP-provider scenarios MUST cover successful compaction and continued execution, oversized inputs, invalid summaries, provider failure, cancellation, persistence interruption, and exhaustion of the compaction budget. They MUST verify that permissions and budgets are unchanged except for recorded consumption and that history/source links survive recovery. Live-model evaluation of summary quality remains separate from these mandatory CI checks.

---

# 17. Task system

Each explicit new work request creates a Task. Clarifications, approvals, interventions, and resumes attach to an existing task under section 17.1 rather than silently creating a new budget.

Example:

```rust
struct Task {
    id: TaskId,
    parent: Option<TaskId>,
    agent: AgentId,
    state: TaskState,
    dependencies: Vec<TaskId>,
    context: ContextId,
    budget: Budget,
}
```

Task states:

```text
Pending
Ready
Running
Waiting
Blocked
Stopping
Completed
Failed
Cancelled
```

## 17.1 Messages, attempts, and task inspection

A new work request creates a task. A clarification, approval, budget change, or explicit resume belongs to the selected existing task and MUST NOT silently create a new budget or transfer grants. While a task is running, composer messages MUST be visibly queued as interventions for that task's next safe agent-loop boundary; they MUST NOT dispatch parallel tools or replace an in-flight request. New task is a separate explicit action. Queued interventions remain editable/cancellable before consumption and MUST preserve their order and task identity.

Tasks, execution attempts, and individual tool operations MUST have separate state/outcome records. Queued and waiting states require machine-readable reasons, such as workspace ownership, model capacity, permission, or user input. Crash-interrupted attempts use `Interrupted`; an operation without a durable result uses `unknown`, neither of which implies a successful task or a safe retry. `Completed` requires the task's declared verification contract or an explicit recorded verification waiver; passing tests from an obsolete workspace revision are not current verification. The fixture acceptance test does not permit such a waiver.

The MVP Tasks menu MUST list task identity, session/workspace, state/reason, current action, elapsed budget, and pending interventions. Selecting a task opens its conversation, activity, partial diff, verification, errors, and trace link without acquiring writer ownership, resuming, changing grants, or redirecting another task's input. List/detail views MUST support incremental loading and bounded render memory; this is ordinary history inspection, not a semantic-memory subsystem.

## 17.2 Graceful cancel and force stop

The Tasks menu and headless CLI MUST expose separate Cancel and Force stop (kill) actions scoped to an explicit task ID. Cancelling a queued task removes it without dispatch. For an executing task, Cancel stops new work, invalidates pending actions/approvals, closes provider requests best-effort, and requests graceful termination of owned tool process groups. The initial grace period is 5 seconds, configurable in `.fluzo` and normal settings. Work that has not terminated after the grace period remains visibly stopping/blocked with a reason; Force stop is offered rather than pretending cancellation completed.

Force stop requires a deliberate user action with a confirmation identifying the task, processes, and risk of partial effects; this is a task-control confirmation, not a tool-authorization prompt bypassed by YOLO. On Linux it escalates to forcible termination of verified owned process groups, including descendants where ownership is established. It MUST NOT kill Fluzo itself, unrelated processes, model servers, collectors, or shared infrastructure, and MUST NOT trust a saved PID alone. A cancelled task with confirmed termination records the graceful/forced termination mode. Unconfirmed local side effects or remote completion remain explicit unknown outcomes; associated workspace ownership/capacity cannot be released optimistically.

Headless force stop MUST require explicit `--yes`; otherwise it returns `confirmation_required` without waiting indefinitely. Requests targeting work owned by another Fluzo process MUST use a private, owner-verified control channel or be refused, not signal arbitrary processes inferred from a task label.

Both actions MUST preserve partial edits, output already captured, and audit intent/outcomes; neither is rollback. Runtime control MUST remain responsive during a blocked provider/tool call. Selecting or dismissing a dialog MUST never execute the action accidentally. Deterministic tests MUST cover a queued task, a cooperative process, a process ignoring graceful termination, descendants, uncertain remote inference, repeat cancellation, and attempts to target an unrelated process.

---

# 18. Multi-agent orchestration

Fluzo MUST support multiple agents working on the same high-level task.

Example:

```text
                  FEATURE
                     │
              ┌──────┴──────┐
              ▼             ▼
         ARCHITECT       SECURITY
              │
              ▼
            CODER
              │
              ▼
            TESTER
              │
              ▼
           REVIEWER
```

The task graph must support:

* dependencies
* parallel execution
* retries
* cancellation
* delegation
* human approval
* failure propagation

---

# 19. Teams

Teams are reusable collections of agents and orchestration rules.

Example:

```toml
[team.feature]

agents = [
    "architect",
    "coder",
    "tester",
    "reviewer"
]

strategy = "pipeline"
```

Potential strategies:

```text
pipeline
parallel
debate
review
hierarchical
dynamic
```

---

# 20. Skills

Skills represent reusable knowledge/instructions.

Example:

```text
skills/
├── rust/
├── kubernetes/
├── azure/
├── security/
├── testing/
└── architecture/
```

Agents can reference skills:

```toml
[agent]
name = "rust-coder"

skills = [
    "rust",
    "testing"
]
```

---

# 21. Execution backends

Fluzo should abstract where tools execute.

```rust
trait ExecutionBackend {
    async fn read_file(...);
    async fn write_file(...);
    async fn execute(...);
    async fn git(...);
}
```

Initial backend:

```text
Local
```

Future backends:

```text
Docker
Podman
SSH
LXC
Proxmox
Kubernetes
Remote
```

This abstraction is important for eventually supporting isolated development environments.

## 21.1 Task workspace strategy

The MVP MUST run the native agent directly in the user's current Git working tree (`in_place`). A future release MUST also support an isolated Git worktree per task (`isolated_worktree`), including single-agent tasks. This is a planned capability, not only an open multi-agent option; its release milestone remains to be scheduled.

Each task MUST have an explicit workspace root and workspace strategy. File tools, shell working directories, Git operations, context discovery, permission boundaries, verification, and diff generation MUST use that assigned root rather than implicitly using the application's startup directory. The initial implementation only needs the `in_place` strategy; worktree provisioning is outside the MVP. Workspace identity and strategy MUST be persisted and included in diagnostic traces without exposing raw paths by default.

In-place execution MUST NOT automatically create or switch branches, create worktrees, stash changes, stage files, commit, or push. Before execution, the runtime MUST establish a baseline of staged, unstaged, and untracked changes and relevant file fingerprints. In normal mode, native editing tools MUST require explicit approval before modifying, deleting, or renaming a file with pre-existing user changes. Approval MUST be scoped to the proposed operation and observed file version, not blanket permission to discard user work. Explicit session YOLO authorization substitutes for individual approval as defined in section 12.2, without disabling version checks or protection against unrelated changes.

Before applying a native edit, the runtime MUST check that the target matches the version read for that edit, including absence when creating a file. A detected external change MUST invalidate the edit and its version-specific approval; the agent must reread and reassess. The UI MUST distinguish pre-existing changes from observed task changes and report uncertainty when external edits prevent reliable attribution. These checks do not provide exclusive filesystem ownership against external editors.

Shell operations remain subject to their own permissions. Commands that may overwrite user changes require explicit approval. Approved scripts can execute arbitrary repository code; native edit checks MUST NOT be presented as constraining every shell side effect or as operating-system sandboxing.

The workspace ownership, path-confinement, and process contracts in sections 21.2 and 21.3 apply to the MVP. Shell approval may come from normal grants or explicit session YOLO, but neither bypasses these contracts.

Cancellation MUST stop scheduling new actions, invalidate pending approvals for the cancelled attempt, cancel provider requests, and request termination of owned tool processes and their descendants where supported. Termination MUST have bounded grace periods and report processes or remote requests whose termination cannot be confirmed. Closing a model connection does not guarantee that remote inference stops.

Cancellation MUST preserve applied edits and known partial outcomes, persist cancellation, and present the partial diff and verification status. It MUST NOT automatically reset, restore, clean, or roll back the workspace, nor imply that completed command side effects are reversible. Cancelling a task MUST NOT stop independently managed model servers or the observability stack.

For the future isolated-worktree strategy, branch/base selection, handling of a dirty source tree, dependency setup, review and integration, conflict resolution, resume, and cleanup require explicit design before implementation. Uncommitted source changes MUST NOT be assumed to appear in a new worktree. Integration into the user's branch and deletion of unmerged work MUST require explicit approval. Worktrees isolate working files, not processes, network access, or shared Git metadata; they are not a security sandbox.

## 21.2 Single writer and native workspace confinement

The MVP MUST allow at most one active writing task per workspace, across sessions and Fluzo processes on the same host. The runtime MUST acquire exclusive workspace ownership before establishing the execution baseline and retain it across dependent edits, verification commands, and approval waits. Shell scripts and tests are potentially writing operations unless a stronger execution boundary proves otherwise. Serializing model requests is not a substitute for this workspace ownership.

Workspace identity MUST use the resolved working-tree root and filesystem identity rather than a project name or unnormalized path. A second writing task MUST remain explicitly queued or blocked without dispatching tools; inspection of persisted history remains available. Ownership may be released only at a durable, quiescent checkpoint with no owned mutating processes or uncertain writers. Resuming requires reacquisition and workspace reconciliation. Crashed/stale owners MUST be reconciled, not replaced solely because a PID or timeout appears stale. Fluzo cannot exclude edits by the user or unrelated applications and MUST retain the external-change checks in section 21.1.

The future worktree strategy MUST assign one writing task to each worktree; independent worktrees may execute concurrently within each owning runtime's configured model/pool limits. Limits are not shared across runtime processes, and the user is responsible for their aggregate inference load. Shared Git metadata and integration operations still require separate coordination. This future allocation does not enable concurrent writers to the current in-place workspace.

Native read/search/edit tools MUST implement a logical workspace jail: permitted paths resolve beneath the assigned root. They MUST reject traversal or symlink/magic-link resolution outside it, enforce containment for new-file parent directories, and reject special files such as device nodes or sockets. Writes to multiply linked files require rejection or an explicit safe copy-on-write strategy so a hard link cannot modify content outside the root. A string-prefix test or a canonicalize-then-open check alone is insufficient; use root-relative filesystem handles or an equivalent race-aware facility and fail closed when the necessary confinement cannot be established.

Agent-directed access to `.git`, `.fluzo`, `.fluzodrive`, and Fluzo's user credential store MUST be separately protected. Git operations use the dedicated policy-controlled Git interface; configuration changes use the user-facing settings flow. Approved configuration/artifact infrastructure can access its own managed paths, but these are not generic agent workspace tools. Ignore files are discovery preferences, not access control. Deterministic tests MUST cover traversal, internal/external symlinks, path replacement races, nonexistent targets, hard links, and protected paths.

This jail constrains native tool APIs, not an approved local shell process or hostile programs running as the same OS user. The TUI MUST identify local shell execution as unsandboxed. Restricting `cwd` is not a filesystem jail, and the MVP MUST NOT claim otherwise. OS-enforced isolation of arbitrary commands is a future sandbox capability under section 21.4.

## 21.3 Child-process input and injected environment

Tool subprocesses MUST start with closed standard input and captured stdout/stderr; they MUST NOT inherit the TUI's controlling terminal or receive a PTY in the MVP. Interactive commands are unsupported in this phase and MUST receive an EOF/error or a bounded timeout, without stealing keystrokes from the application. The owning runtime MUST track process groups and descendants for cancellation independently of display state.

The child environment MUST be built explicitly, not copied wholesale from Fluzo's process. A documented baseline may include required locale, toolchain, temporary-directory, and user-home settings. Provider/OTLP credentials, authentication sockets, loader/startup overrides, and unrelated environment secrets MUST NOT be inherited by default. In particular, shell startup files and variables such as `BASH_ENV` MUST NOT silently inject commands. The approved executable and arguments MUST be resolved against the effective environment; an implicit workspace `.` in executable search paths MUST NOT broaden an approval.

The repository `.fluzo` and normal TUI settings MUST support non-secret environment values and individually authorized environment references for tools. Secret references resolve through the user credential mechanism at dispatch, never by embedding values in project configuration. New or changed injection scopes MUST be reviewed with the command/environment fingerprint and MUST invalidate affected approvals. Environment values that are sensitive MUST remain redacted in UI, logs, and records. Removing automatic inheritance reduces accidental exposure but cannot stop an unsandboxed same-user process reading credentials elsewhere on disk.

Built-in supposedly read-only Git inspection MUST disable external diff/text conversion, filesystem-monitor hooks, pagers, credential prompting, and other configurable external execution paths it does not explicitly require. A repository setting MUST NOT turn automatic context inspection into an unapproved program launch. User-requested Git commands that need external helpers follow the ordinary process/permission path. Tests MUST include a sentinel credential absent from child environments, approved non-secret injection, EOF on stdin, no controlling-TTY access, and repository-supplied helper settings that are not executed during inspection.

## 21.4 Future sandbox evaluation proposal

After the local MVP, evaluate an OS-enforced execution sandbox as a separate capability, not a renamed worktree or a relaxed permission mode. Candidate approaches are rootless containers with optional Dev Container configuration, and Linux namespace/Landlock/seccomp-based tools where supported. The evaluation MUST compare workspace/dependency mounts, network and DNS policy, secret injection, UID mapping, resource limits, process-tree termination, startup cost, and Linux-to-macOS/Windows portability.

A Dev Container definition is environment configuration, not proof of a security boundary. Untrusted lifecycle hooks, privileged containers, host networking, Docker socket mounts, and arbitrary host bind mounts MUST require separate scrutiny and cannot be accepted as safe defaults. The proposed baseline is an explicitly permitted writable task workspace, read-only or isolated dependencies, no host credentials/socket, disabled network unless granted, and finite CPU/memory/process limits. Adversarial fixtures MUST test escape and cleanup behavior before any isolation guarantee is advertised. Backend selection and exact guarantees remain a future reviewed design decision.

---

# 22. Storage

SQLite should be used for persistent runtime state.

Initial entities:

```text
projects
sessions
messages
tasks
agents
agent_runs
tool_calls
routing_decisions
permissions
artifacts
events
```

SQLite should remain local and portable.

## 22.1 Explicit session recovery

The MVP MUST support reopening persisted sessions after a normal exit, cancellation, or crash. Reopening is read-only with respect to agent execution: it MUST NOT contact model or decision providers, execute tools, retry requests, or dispatch queued actions. Both the TUI and headless CLI MUST require an explicit user resume action before starting a new execution attempt; selecting a session alone is not consent to continue.

Recovery MUST present the recorded conversation, task history, known tool results, partial changes, and verification status subject to the session's retention and capture policy. Missing or redacted content MUST be identified rather than reconstructed as if it had been retained. Local session content is application state, not telemetry: storing it MUST NOT authorize including it in spans, logs, or OTLP export. Session retention and content controls MUST be documented separately from diagnostic capture, with the same credential protection and access restrictions.

On recovery, attempts recorded as running without a durable terminal outcome MUST be marked interrupted. Operations that may have started but have no confirmed result MUST be shown as outcome unknown, not failed, successful, or safe to repeat. An operation identifier is not proof that an external side effect happened exactly once. The runtime MUST persist operation intent before dispatching a side-effecting tool call and its outcome after completion; failure to persist intent MUST prevent dispatch. This journal exposes uncertainty after a crash but does not make filesystem or shell effects transactional with SQLite.

Before resuming, the runtime MUST revalidate workspace identity, Git branch/revision, and relevant file versions against the recorded state. Changes MUST be surfaced and stale context, verification claims, and edit approvals invalidated as appropriate. A missing or mismatched workspace MUST block continuation until explicitly resolved; the runtime MUST NOT silently substitute its current startup directory. Inspection after the user's resume request MUST remain non-mutating until the reconciliation is complete.

Pending permission requests and unused operation-specific approvals from the interrupted attempt MUST NOT carry over. Deliberately configured standing grants remain subject to current policy and scope checks. Resuming alone MUST NOT authorize replay of an operation with an unknown outcome. Such an operation requires reconciliation using available evidence or explicit user approval to retry with its possible duplicate side effects disclosed. Recovery MUST NOT blindly kill processes using persisted process IDs, which may have been reused; uncertain process ownership or termination MUST be reported.

Explicit resume MUST create a new attempt and trace linked to the original task/session and prior attempt. Known budget consumption MUST carry forward rather than reset silently; uncertain usage MUST be disclosed and any budget extension made explicit. Reconciliation and recovery decisions MUST be persisted and observable. Automatic rollback and automatic command replay are outside the MVP recovery contract.

## 22.2 Retention and cleanup

The default is to retain all permitted captured session history, artifacts, Laya evaluation records, and local diagnostic archives until explicitly deleted, without automatic age-based expiry. Session content includes user/assistant conversation, tool requests/results, edit diffs, verification, and summaries needed for recovery. It is not a backup of the repository or a requirement to capture private model reasoning. Secrets MUST be redacted before persistence; omitted/redacted/truncated content MUST be marked. Retention does not remove finite per-output capture limits.

Session databases, conversations, artifacts, and local diagnostics MUST live in the selected repository's `.fluzodrive/` directory, not a global history store. The default layout is `.fluzodrive/state.sqlite3`, `.fluzodrive/artifacts/`, and `.fluzodrive/telemetry/`. Project identity and session IDs MUST be persisted; moving/cloning a repository does not automatically transfer endpoint trust or authorize old work to resume. The `.fluzo` file contains settings, never database/history payloads.

Before creating private data, initialization MUST verify that `.fluzodrive/` is not tracked and is excluded from Git. The wizard MUST offer a confirmed local `.git/info/exclude` entry resolved through Git's actual metadata location, or accept an existing suitable ignore rule. It MUST NOT silently modify the tracked `.gitignore`, untrack previously committed data, follow a data-root symlink, or reuse an arbitrary directory as its private store. A tracked/unprotected store blocks persistent execution with a clear repair action; isolated demos may still run. `.fluzodrive/` MUST be excluded from agent discovery/context and protected from generic file tools independently of Git ignore rules. Git exclusion is not encryption and cannot prevent deliberate force-adds.

On Linux, managed data directories/files MUST use owner-only permissions (0700/0600 where applicable). The user-level file `${XDG_CONFIG_HOME:-~/.config}/fluzo/auth.toml` is reserved for provider authentication references and explicitly opted-in local credentials, not repository configuration defaults. Environment references are preferred; literal credential storage, if used, requires an explicit disclosure that the file is not encrypted, restrictive permissions, and endpoint-scoped references. Project `.fluzo` files MUST never contain literal credentials. Minimal endpoint/workspace trust records and same-host workspace-writer ownership/control state may also live in protected user-local state; they do not provide global task/storage limits, shared inference-slot allocation, or conversation storage. Same-user processes can still read local files, and the MVP MUST not imply protection against them.

Initial configurable storage guardrails are 10 GiB for this repository's session data/artifacts, 2 GiB for its local diagnostics, a warning at 80% utilization, and a 1 GiB free-space reserve on the hosting filesystem. These values are scoped to `.fluzodrive/` and configured only by this repository's `.fluzo`; changing one project's quota MUST NOT reconfigure or purge another project's store. The free-space check is a safety check on a potentially shared disk, not an exclusive reservation. These are admission thresholds, not hard filesystem quotas: in-flight writes, SQLite journals, and filesystem overhead require headroom. At the session threshold, stop admitting new state-mutating work before its required audit state cannot be recorded. At the diagnostic threshold, retain existing data and report newly dropped telemetry/degraded capture without blocking ordinary execution; mandatory audit persistence failure still blocks the task. Never silently evict retained data. The user can explicitly purge or increase the limits through section 26.2.

Required cleanup commands are:

```bash
fluzo history list
fluzo history purge --session <id> --dry-run
fluzo history purge --session <id>
fluzo history purge --all --yes
fluzo telemetry purge --local --dry-run
fluzo telemetry purge --local --yes
```

History deletion MUST remove selected session records and exclusively owned artifacts, including summaries/evaluation records, while preserving shared artifacts still referenced by another session. `--all` means every session in the explicitly selected repository only; the preview MUST name that repository and `.fluzodrive/` path. Commands MUST NOT scan or delete other repositories, user authentication files, or global trust/ownership records implicitly. Telemetry deletion targets that repository's local diagnostic archive and pending export buffers separately; history deletion MUST NOT imply that diagnostic copies were removed. Dry-run MUST be side-effect free. Actual deletion requires confirmation or explicit `--yes`, even in YOLO; non-interactive deletion without confirmation MUST return promptly without deleting data.

Active/attached sessions MUST be protected until stopped/detached. Telemetry deletion MUST quiesce relevant writers/exporters or refuse; stale buffers MUST NOT immediately repopulate a purged archive. Partial failures MUST be reported, and deletion MUST be idempotent/retryable without damaging surviving records. Artifact traversal MUST remain within managed roots and not follow symlinks into user data. Cleanup MUST NOT delete the workspace, `.fluzo`, credentials, or unrelated volumes. SQLite maintenance and logical deletion do not guarantee forensic erasure from storage, backups, or snapshots.

Already exported records remain under backend ownership. The reference Compose environment MUST document an explicit destructive cleanup scoped to its dedicated telemetry volumes, with affected destinations/data listed before confirmation. Local purge MUST NOT claim to erase remote data, shared backends, or per-session aggregate metrics. External deletion and backup cleanup are separate administrative actions, and the result MUST state which stores were and were not cleared.

---

# 23. Event model

All important runtime actions should produce events.

Example:

```rust
enum Event {
    UserMessage,
    TaskCreated,
    TaskStarted,

    AgentStarted,
    AgentMessage,
    AgentCompleted,
    AgentFailed,

    ToolRequested,
    ToolExecuted,

    PermissionRequested,
    PermissionGranted,
    PermissionDenied,

    RoutingDecision,

    VerificationStarted,
    VerificationPassed,
    VerificationFailed,

    TaskCompleted,
    TaskFailed,
}
```

Events should be serializable.

---

# 24. Replay

The runtime MUST preserve enough information to reconstruct the recorded execution timeline, subject to retention and privacy limits. Replay is a read-only rendering of persisted events: it MUST NOT call providers, execute tools, restore files, or resume a task. Deterministic replay means consistent reconstruction from the same recorded events, not deterministic re-execution of models or external side effects. Gaps and unknown outcomes MUST remain visible. Continuing work uses the separate explicit-resume contract in section 22.1.

Example:

```bash
fluzo replay task-123
```

Expected output:

```text
08:31 router → architect
08:31 architect started
08:33 architect → coder
08:34 coder requested shell
08:34 policy → allow
08:36 coder → tester
08:37 tests failed
08:37 router → coder
08:39 tests passed
08:40 reviewer started
08:42 reviewer completed
```

Replay is both a debugging feature and a development tool for Fluzo itself.

---

# 25. Loop detection

The Harness should detect repetitive agent behaviour.

Example:

```text
edit
test
fail
edit
test
fail
edit
test
fail
```

The system should be able to invoke a decision provider:

```json
{
  "decision": "replan",
  "confidence": 0.94
}
```

Possible actions:

```text
continue
retry
replan
delegate
ask_user
abort
```

---

# 26. Configuration

The canonical project configuration MUST be a single TOML file named `.fluzo` in the selected workspace root. Every supported persistent option MUST have a typed, versioned schema entry, including model endpoints, per-model/pool concurrency, context, execution limits, permissions, storage, telemetry, TUI, notifications, devmenu, and implemented UI flags. The wizard MUST write supported non-secret defaults explicitly. Large artifacts and skills may be referenced by path, not embedded in the configuration file.

Ordinary setting precedence is built-in defaults, the selected repository's `.fluzo` (or explicit `--config` file scoped to that workspace), and explicit CLI overrides. There is no inherited global Fluzo configuration for limits, UI, models, or storage. User-level authentication and private consent/coordination state are separate concerns under section 22.2, not an extra settings layer. Configuration is data only: no executable includes, shell interpolation, or command substitution. Unknown keys, invalid types/ranges, and unsupported schema versions MUST produce actionable diagnostics.

Project secret settings MUST reference a named environment variable or an endpoint-scoped entry in the user's authentication file, never a literal credential. Authentication may be explicitly disabled for a trusted local endpoint. New or changed sensitive destinations, standing grants, injected tool environments, or content-export settings require user review; consent is stored privately and scoped to the workspace and relevant configuration fingerprint. A downloaded file or copied `.fluzodrive/` is not authorization to send data or execute tools. Unchanged trusted configuration MUST NOT repeat initialization. Non-interactive execution without required consent MUST fail closed without contacting configured destinations. Non-loopback HTTP model endpoints require an explicit warned, endpoint-scoped exception; private server addresses MUST NOT ship as defaults. Redirect prohibition in section 42.1 still applies after endpoint approval.

Project configuration MAY narrow permissions but MUST NOT override explicit user denials or broaden grants/content export without user authorization. The permission table is a requested per-repository policy, not a global authority. YOLO remains transient session state, not a persistable startup default. `tui.dev_menu = true` is a supported persistent presentation preference and confers no runtime privileges.

## 26.1 Welcome and setup

Without a selected config file, interactive startup MUST show a polished welcome screen and wizard for generative endpoint/model, credential reference, context/output capacity, per-model/shared-server slots, optional Laya shadow service, data preferences, optional OTLP export, theme/animation, and devmenu. Advanced settings MUST be available without forcing every option into the mandatory first-run sequence. A redacted summary and target path MUST precede atomic creation of `.fluzo`.

Connection tests require explicit user action and synthetic inputs, with finite timeouts and a clear distinction between model discovery and potentially chargeable inference. Saving offline and opening a model-independent demo MUST be supported. A valid existing file MUST skip setup. Unavailable services or credentials produce targeted repair guidance, not a fresh wizard. Malformed files MUST be preserved and diagnosed by path/key; explicit repair/migration MUST provide a recoverable backup rather than overwrite silently.

`fluzo init` explicitly invokes setup, with confirmation before replacing an existing file. Non-interactive startup without config MUST return a nonzero `configuration_required` result, not launch a wizard. Tests/demos MUST isolate their config and never modify the user's file. The wizard MUST explain that `.fluzo` can reveal infrastructure/preferences even without secrets; committing it or changing Git ignore rules is the user's decision.

## 26.2 TUI settings and limit changes

The normal TUI MUST provide Configuration > Limits and Configuration > Models, without requiring devmenu. All configured execution, context, request, model/pool capacity, storage, and telemetry limits MUST be editable using typed controls with units, defaults, saved/effective values, provenance, and consequences. The UI MUST validate related constraints together and support Cancel and Restore defaults.

Save MUST write to the active `.fluzo` atomically, preserving unrelated values and comments where practical. External changes require reload/reconciliation rather than clobbering the file. Failed saves MUST leave the previous configuration and runtime state intact. CLI overrides MUST be visibly identified and remain authoritative for that invocation; saved future defaults MUST NOT silently replace them.

Operational changes apply to future work by default. Applying to an active task/runtime requires an additional explicit user action that previews the new limits and current consumption; consumption MUST NOT reset. Limits below consumed budget MUST block further work through the existing exhaustion flow. In-flight requests keep their dispatched deadlines; lower slot limits drain naturally as specified in section 43.3. Resuming blocked work remains explicit, also in YOLO. External or agent-authored config edits MUST NOT silently enlarge an active allocation. Applied changes MUST be recorded in versioned effective-configuration snapshots and redacted audit events.

Tests MUST cover UI/file round trips, defaults and reload, invalid combinations, failed writes, external edits, CLI precedence, future-versus-current scope, and preserved consumption. The devmenu uses this persistence mechanism for UI preferences only and MUST NOT become a shortcut for operational/security changes.

---

# 27. Example configuration

Illustrative MVP `.fluzo`. Local URLs are examples, not servers installed automatically. The wizard emits the complete supported schema; these conservative slots are not measurements of the user's server.

```toml
schema_version = 1

[project]
name = "my-project"

[agent]
runtime = "native"
model = "coder"

[models.coder]
provider = "openai_compatible"
base_url = "http://127.0.0.1:8080/v1"
model = "flash-halogen"
auth = "none"
context_window = 32768
max_output_tokens = 4096
capacity_id = "local-flash"
pool = "local_server"
max_in_flight = 1

[models.laya]
provider = "laya_systemone"
endpoint = "http://127.0.0.1:8080/upstream/laya/v1/systemone"
auth = "none"
capacity_id = "local-laya"
pool = "local_server"
max_in_flight = 1

[capacity_pools.local_server]
max_in_flight = 1
foreground_reserved_slots = 1
queue_capacity = 8
queue_timeout_seconds = 30

[decision]
enabled = false
mode = "shadow"
model = "laya"
timeout_seconds = 5
max_observations_per_task = 30
failure_pause_threshold = 3

[harness]
max_turns = 30
max_active_seconds = 1200
shell_timeout_seconds = 120
provider_retries = 2
max_tool_calls = 100
max_total_tokens = 200000

[tools.shell]
stdin = "closed"
termination_grace_seconds = 5
inherit_env = []
env = { RUST_BACKTRACE = "1" }

[policy]
shell = "ask"
tool_network = "deny"
git_commit = "ask"
git_push = "ask"

[context]
compaction_threshold = 0.8
compaction_max_output_tokens = 2048
tool_context_max_bytes = 65536
tool_capture_max_bytes = 2097152

[storage]
auto_expire = false
session_max_bytes = 10737418240
diagnostic_max_bytes = 2147483648
min_free_bytes = 1073741824

[telemetry]
export_enabled = false
otlp_protocol = "http/protobuf"
otlp_endpoint = "http://127.0.0.1:4318"
capture_content = false

[tui]
theme = "default"
animation_fps = 60
reduced_motion = false
dev_menu = false

[tui.notifications]
desktop_enabled = false
duration_seconds = 5
max_visible = 3

[tui.flags]
render_diagnostics = false
```

Authenticated models use `auth = "env"` with `api_key_env`, or `auth = "credential"` with an endpoint-scoped `credential_ref` from user-local authentication, not literal credentials. Shell `env` contains non-secret literals; `inherit_env` lists specifically reviewed additional parent variables, not unrestricted inheritance. Reserved provider/telemetry secrets are excluded; tool-specific secret injection uses separately authorized credential references under section 21.3. The 32768-token context is an onboarding suggestion requiring confirmation for the selected model. Separate capacity pools or higher slot counts require explicit resource allocation; assigning Halogen and Laya to one pool preserves the default shared-server ceiling. Active model routing, ACP teams, and multi-agent options are outside this MVP example.

---

# 28. CLI

The MVP CLI MUST support the following contracts, alongside the interactive TUI:

| Command | Behavior |
| ------- | -------- |
| `fluzo` | Open the TUI, or welcome/setup when no config exists |
| `fluzo init` | Explicit configuration wizard; replacement requires confirmation |
| `fluzo config edit` | Open typed settings and save to the selected `.fluzo` |
| `fluzo config show --effective` | Show effective values and sources, with secrets redacted |
| `fluzo run "fix the failing test"` | Run a native-agent task with headless permission/admission rules |
| `fluzo session list` | List persisted sessions |
| `fluzo session open <id>` | Open history without starting execution |
| `fluzo session resume <id>` | Explicit continuation, reconciliation, and admission checks |
| `fluzo task list` | List task outcomes, including blocked/queued status |
| `fluzo task show <id>` | Inspect activity, interventions, verification, and task diagnostics without execution |
| `fluzo task cancel <id>` | Request graceful cancellation of the identified task |
| `fluzo task kill <id>` | Deliberately force-stop owned local work with the confirmation in section 17.2 |
| `fluzo replay <task-id>` | Read-only reconstruction from recorded events |
| `fluzo history list` | List retained history and storage usage |
| `fluzo history purge ...` | Explicit cleanup under section 22.2 |
| `fluzo telemetry purge --local ...` | Separate local telemetry cleanup under section 22.2 |
| `fluzo doctor` | Local configuration/dependency validation; network probes require explicit opt-in |
| `fluzo demo` | Isolated deterministic UI scenarios without real inference |

Invocation controls MUST include `--config`, `--dev-menu`/`--no-dev-menu`, `--animation-fps`, and explicit session-scoped `--yolo` where applicable. Read-only commands MUST NOT call providers. Headless results MUST distinguish success, configuration/permission requirements, budget exhaustion, capacity queue failures, cancellation, and unknown outcomes through structured status and nonzero failure exits. Numeric exit codes MUST be documented with the implementation.

Named external-agent selection, `fluzo agent list`, and `fluzo team run` belong to later interoperability/orchestration releases. These are planned command contracts, not claims that binaries or tests already exist. Build, deterministic/live test-profile, and packaging commands MUST be documented as those implementations are delivered.

---

# 29. TUI

English is the initial language for TUI labels, onboarding, configuration help, notifications, CLI help, and application-generated diagnostic messages. User messages, source code, tool output, and model responses MUST retain their original language; English UI does not restrict the language of a task. User-facing strings MUST be organized for later localization without requiring a translation framework or additional locales in the MVP.

Visual quality and interaction quality are primary product requirements and MVP release gates, not post-MVP polish. The primary reference is [Crush](https://github.com/charmbracelet/crush), specifically its expressive color treatment, terminal-native composition, notifications, and interactive feel. Fluzo MUST aim for a comparably polished experience while retaining its own identity and the runtime/security contracts in this PRD. This reference does not imply adopting Crush's implementation, full feature set, or permission semantics.

## 29.1 Visual direction

The default theme MUST be intentionally art-directed: expressive accent colors, a coordinated neutral background/foreground hierarchy, restrained borders, clear focus, and distinct semantic colors for activity, success, warning, error, and permission mode. Color MUST organize information rather than decorate every surface equally. Markdown, code, diffs, tool results, dialogs, and notifications MUST share a consistent theme-token system. Terminal typography relies on spacing, weight, and contrast rather than requiring a particular installed font.

The MVP MUST include a polished default theme and a readable high-contrast alternative, with terminal-capability-aware color fallback. A theme picker MUST preview changes and restore the prior theme on cancellation. A large theme catalog and theme editor are not MVP requirements. Required statuses MUST also use labels or symbols, never color alone; normal/YOLO mode MUST remain unambiguous. No essential interaction may depend on a Nerd Font, emoji rendering, or truecolor support.

The screen MUST prioritize the conversation and current work, with compact status and secondary details revealed on demand. It MUST NOT become a wall of equally weighted panels or raw logs. Loading, empty, streaming, waiting-for-approval, blocked, cancelled, failed, recovered, and completed states MUST have deliberate layouts rather than placeholder output. The first screen is the usable session or setup flow, not a decorative splash that delays interaction.

## 29.2 Interaction quality

The TUI MUST provide a searchable command palette, discoverable keyboard actions, visible focus, and keyboard-only access to every core workflow. Optional mouse support MUST complement, not replace, keyboard navigation. Composer behavior MUST support multiline editing and safe bracketed paste without accidentally submitting pasted commands or text. Drafts and scroll position MUST survive opening and closing secondary views.

Streaming content and tool updates MUST NOT steal focus or pull a user away from older messages they are inspecting. Following live output MUST be an explicit recoverable view state, with an indication of new activity when scrolled away. Tool details MUST expand/collapse in place, and long output MUST be bounded without hiding failures or truncation indicators. Code and diffs MUST remain readable and selectable/copyable where terminal capabilities permit, with clear fallback behavior.

Motion MUST communicate real activity or state transitions through restrained indicators, never simulated progress or compulsory decorative animation. Reduced-motion mode MUST be available. Model inference, telemetry export, large diffs, and streaming updates MUST NOT block input handling or cancellation. The existing input-latency target MUST be measured under a documented synthetic streaming workload, not only on an idle screen.

### 29.2.1 Animated pixel-art identity

The MVP visual/interaction prototype MUST include an original pixel-art logo inspired by a stylized Y-shaped flux condenser. It MUST have its own artwork rather than reproduce the film prop exactly. The logo MUST occupy a compact, fixed-size header area with responsive variants that do not displace the composer, permission controls, or task information. Animation MUST NOT change its layout dimensions or delay startup behind a splash screen.

Logo states MUST follow actual runtime state: a static dimmed idle state, inward-moving pulses during execution, a slow amber pulse while waiting for user input, a brief non-flashing completion highlight, and distinct error/cancellation transitions. Associated text MUST identify state independently of color or animation. These are activity cues, not a claimed completion percentage. Animation speed MUST use elapsed monotonic time so lowering the frame rate does not lengthen the state transitions.

The default animation target MUST be 60 frames per second while motion is active. This is a scheduling target and upper bound for animation-driven redraws, not a guarantee of terminal/display presentation rate. The TUI MUST accept `--animation-fps <integer>` and a persistent `[tui] animation_fps` setting. Valid values are 0 through 60: 60 is the default, 30 and 15 are documented lower-cost options, and 0 disables animated motion while preserving immediate static state updates. Invalid values MUST produce an actionable configuration error. An explicit CLI value overrides the configured rate; reduced-motion mode MUST disable animated motion regardless of the selected rate.

For example:

```bash
fluzo --animation-fps 60
fluzo --animation-fps 30
fluzo --animation-fps 0
```

```toml
[tui]
animation_fps = 60
```

Rendering MUST use terminal-native colored block glyphs through Ratatui, with a simple fallback for unsupported glyph/color capabilities. GIF playback, terminal image protocols, and special fonts MUST NOT be required. Artwork resolution and cell aspect ratio MUST be checked in the supported terminals rather than assumed to match square screen pixels.

The animation clock MUST be independent of model tokens, tool execution, and telemetry export. There MUST be one coordinated terminal writer with bounded redraw scheduling, coalesced visual updates, and differential output where supported; a logo tick MUST NOT trigger unnecessary recomputation of the entire conversation. Slow rendering MUST skip obsolete animation frames rather than queue catch-up work. Input and runtime events MUST be processed promptly, not gated by the animation setting. Static idle states MUST NOT keep a 60 Hz animation timer running, and CLI/headless runs MUST NOT animate. No per-frame domain events, trace spans, or log records may be emitted; aggregate performance measurements are sufficient.

### 29.2.2 Developer menu and local UI feature flags

The MVP prototype MUST include a keyboard-accessible, searchable Developer Menu for tuning visual behavior without rebuilding the application. It MUST be enabled with `fluzo --dev-menu` or saved `tui.dev_menu = true` in `.fluzo`, and opened through the command palette. `--no-dev-menu` disables it for an invocation. It is disabled by default, available in ordinary developer installations rather than only debug builds, and MUST NOT depend on an external feature-flag service or model availability.

The menu MUST distinguish typed presentation settings from boolean experimental UI flags and the explicitly permitted Laya shadow-observer control. The initial controls MUST cover:

* animation FPS (0 through 60), reduced motion, logo pulse speed/intensity within safe non-flashing bounds, and implemented compact logo variants
* theme selection and a small set of accent/contrast presets, without requiring a full theme editor
* in-app notification duration and maximum visible stack within validated layout limits, plus notification enablement preferences
* implemented layout-density and tool-detail presentation variants
* a rendering diagnostics overlay with aggregate redraw cadence, frame duration, and skipped-frame counts, clearly distinguished from display FPS
* Laya observation enable/disable via `decision.enabled`, with capacity reservation, effective status, and shared-resource warnings visible

Boolean flags MUST use toggles, numeric settings MUST use bounded inputs/steppers, and enumerated settings MUST use selectors. Only implemented variants may appear as selectable features. Every entry MUST show its stable key, purpose, default, effective value, source, and whether it supports live application or requires restart. The settings/flag registry MUST define types, valid ranges, and defaults consistently for configuration loading and the menu; arbitrary configuration keys or executable expressions MUST NOT be accepted.

Live previews MUST be temporary by default and preserve composer drafts, focus restoration, scroll position, and task execution. The menu MUST provide Apply for session, Save to .fluzo, Cancel/revert preview, and Reset to defaults actions. Closing without applying MUST revert the preview. Saving MUST follow section 26.2 and modify only selected UI preferences. Persistent UI defaults MUST NOT contain temporary demo state. Explicit CLI overrides such as `--animation-fps` remain authoritative and MUST be shown as locked rather than silently overwritten; reduced-motion and terminal capability restrictions take precedence over animation flags. Restart-required changes MUST be labeled pending and MUST NOT restart an active session automatically.

Test notifications, simulated logo/task states, and reproducible visual scenarios MUST be available only in a clearly labeled isolated demo/preview context driven by synthetic events. They MUST NOT forge actual task outcomes, mutate a real session, send desktop test notifications implicitly, or call real model providers. In a live session, the logo and status indicators MUST continue to reflect the actual runtime state.

Developer flags are limited to presentation/diagnostics, with `decision.enabled` as a deliberate exception for optional shadow observation. That control MAY cause real Laya requests only in an authorized live session with sufficient reserved capacity; synthetic demos and CI remain isolated and MUST NOT call real services. It MUST use the same validated setting/consent path as normal settings, not a hidden flag. No devmenu control may enable YOLO, bypass approvals, alter budgets/pool allocations or verification, activate live-test profiles, disclose secrets, change capture/export consent, or enable active routing. No flag may hide effective permission mode or required failure/approval state. The menu is not a general runtime configuration editor.

Applied changes MUST emit redacted configuration-change diagnostics, not per-frame logs. Effective UI settings and flag versions MUST be available in sanitized diagnostic exports and deterministic test fixtures so visual reports can be reproduced. Unknown or retired flags MUST produce an actionable diagnostic, never silently enable another behavior. Tests MUST cover live changes, preview rollback, session-only versus saved values, invalid input, CLI precedence, restart-required state, and isolation from runtime authorization and real-provider execution.

### 29.2.3 Untrusted terminal content: MVP and future hardening

For the MVP, model text, source files, filenames, tool output, provider errors, and persisted history MUST be treated as untrusted display data. They MUST never be forwarded to the terminal as raw escape sequences. An incremental, bounded decoder MUST convert permitted styling into application-owned Ratatui spans and escape or discard other controls, including OSC clipboard/title/link commands, cursor movement, device-control strings, and terminal mode changes. Escape sequences split across streaming chunks MUST remain harmless; incomplete sequences MUST NOT create an unbounded parser buffer. The same rule applies to CLI output, replay, notifications, and copy previews.

Only the application's own rendering and explicitly user-invoked clipboard/link actions may issue approved terminal control sequences. Paths and commands in security-sensitive views MUST visibly escape misleading control/bidirectional formatting characters while preserving an exact, safely encoded underlying value for the policy decision. Normal multilingual text remains supported. Tool/model messages MUST have structural origin labels and MUST NOT be able to render a real approval widget or impersonate runtime status. New messages MUST NOT steal approval focus or cause an Enter key intended for the composer to authorize a command.

The MVP test corpus MUST include OSC 52, OSC 8, cursor/erase sequences, carriage-return rewriting, split/incomplete sequences, invalid UTF-8, control-bearing filenames, oversized styled output, and bidirectional-control spoofing of a path. Tests MUST verify both visible output and absence of unauthorized terminal-control bytes. Recordings and snapshots use sanitized content; secret redaction is an additional independent requirement, not a substitute for terminal sanitization.

Future hardening should evaluate property-based and coverage-guided fuzzing of the streaming decoder/render adapters, a broader terminal/multiplexer matrix, and isolated PTY execution for deliberately interactive tools. Rich terminal graphics, clickable links, and interactive subprocess rendering remain capability-checked extensions with explicit user actions and allowlisted protocols. No future rich-output mode may silently permit arbitrary provider/tool escape sequences. This is a reviewable hardening proposal, not an MVP promise of a fully sandboxed terminal emulator.

## 29.3 Notifications

The MVP MUST provide styled in-app notifications with semantic severity, concise text, optional relevant actions, dismissal, deduplication, and bounded stacking. Notifications MUST NOT steal typing focus, obscure the composer or permission controls, or resize the conversation unpredictably. Informational notices may expire; unresolved failures and approval requirements MUST remain discoverable in persistent task/activity state after a toast disappears.

Task completion, execution blocked on user input, and failures MUST be eligible for configurable terminal/desktop notifications when the terminal is unfocused and capability detection supports them. In-app notifications remain the fallback; unsupported focus reporting MUST NOT be treated as proof that the terminal is unfocused. External notifications MUST be disableable and omit prompts, source code, command contents, and sensitive paths by default. A notification MUST never approve an action or resume a session merely by being dismissed. Native notification transport support follows the supported-platform matrix, not a claim of identical behavior in every terminal.

## 29.4 Visual and interaction acceptance

Before accepting the TUI, the project MUST provide a deterministic demo using the existing HTTP simulators, covering conversation streaming, tool expansion, permissions, YOLO state, diffs/tests, session recovery, compaction, limits, errors, and notifications. This allows design review without model access, credentials, or inference cost. A visual/interaction prototype using these scenarios MUST be reviewed before the full screen set is considered settled.

The demo MUST include the pixel-art logo and its runtime-driven transitions at 60, 30, 15, and 0 FPS, plus reduced-motion mode. Deterministic animation tests MUST use a controllable clock, not depend on wall-clock frame timing in CI. Performance review on the documented Arch Linux/CachyOS terminal matrix MUST report CPU usage, render-time distribution, achieved application redraw cadence, and input latency during streaming and idle, with the hardware, terminal, viewport, and animation setting recorded. Application redraw measurements MUST NOT be mislabeled as measured display FPS. The existing input-latency target applies with the default 60 FPS target enabled; missing that target on a documented reference environment requires optimization or an explicit product decision, not silently changing the default. Idle redraw behavior and the configurable lower-rate fallback MUST also be verified.

Automated coverage MUST combine Ratatui buffer snapshots with pseudo-terminal interaction tests for focus, keyboard navigation, resize, scrolling, paste, cancellation, and terminal-state restoration on exit. Baseline layouts MUST be tested at 80x24, 120x40, and 160x50 character cells, including resizing during streaming and notifications. Narrow layouts MUST collapse secondary detail rather than overlap or truncate essential controls; smaller unsupported sizes MUST show a usable resize notice. Long paths, multiline errors, Unicode display widths, and large diffs MUST be included in fixtures.

Screenshots or terminal recordings MUST be reviewed in representative supported terminals with truecolor and reduced-color modes. Automated snapshots alone do not establish visual quality. Release acceptance requires explicit product-owner review of color hierarchy, readability, motion, notification behavior, and end-to-end interaction against the Crush reference, with the reference version and test environment recorded. Visual regressions, lost input, focus jumps, and obscured permission controls are release defects, not optional cleanup.

## 29.5 Future multi-agent sketch

The sketch below illustrates a later multi-agent view, not the MVP layout or its visual acceptance standard.

```text
╭─ Fluzo ───────────────────────────────────────────────╮
│                                                       │
│  ● architect    completed                            │
│  ● coder        running                              │
│  ○ security     waiting                              │
│                                                       │
│  ───────────────────────────────────────────────────  │
│                                                       │
│  User                                                 │
│  Implement OAuth authentication.                      │
│                                                       │
│  ┌─ coder ──────────────────────────────────────────┐ │
│  │ Editing src/auth.rs                              │ │
│  │                                                  │ │
│  │ Running tests...                                 │ │
│  └──────────────────────────────────────────────────┘ │
│                                                       │
│  > Ask anything...                                    │
╰───────────────────────────────────────────────────────╯
```

---

# 30. TUI views

Required MVP surfaces (not necessarily separate full-screen pages):

### Conversation and activity

Main conversation, streaming responses, expandable tool activity, and the current task state. The composer and normal/YOLO indicator MUST remain accessible without navigating to a diagnostic screen.

### Permissions

Integrated approval UI with action, scope, and grant duration; visible pending/denied outcomes and permission history. YOLO mode follows section 12.2 and MUST never be implied only by a theme color.

### Diff and verification

Workspace changes, pre-existing-change attribution where known, and test results, including incomplete verification and partial outcomes after cancellation. Reviewing a diff MUST NOT implicitly stage, revert, commit, or accept changes.

### Sessions

Searchable session selection with task status and explicit separation between opening history and resuming execution. Viewing another session MUST NOT automatically start another agent run or change authorization state.

### Tasks

A searchable task list and task detail view MUST show running, queued, blocked, stopping, and completed work. It MUST offer inspection, graceful Cancel, and deliberate Force stop, following section 17.2. This is an MVP task monitor, not a multi-agent graph/team editor. All mutating tasks remain subject to one writer per workspace. Selecting another task MUST make its identity and the destination of any new input unambiguous.

### Task diagnostics

Errors, budget consumption, compaction events, telemetry health, trace ID, and correlated local events. Laya recommendations MUST be labeled as observations, not actual actions. Grafana MAY provide deeper investigation but MUST NOT be required to use these diagnostics or complete a coding task.

### Configuration access

The command palette MUST expose editable configuration screens for models/shared-server slots, limits, storage, telemetry, theme, notifications, and devmenu, persisting preferences to `.fluzo` under section 26.2. Secret references, not values, are displayed. All supported persistent settings MUST be accessible through typed basic/advanced controls; an embedded raw TOML editor is not required. Runtime permission mode remains a separate session control.

When explicitly enabled, the Developer Menu in section 29.2.2 provides live UI tuning and local presentation flags; it does not replace normal configuration or permission controls.

Task graphs, team management, and multi-agent dashboards are explicitly outside the MVP. The runtime remains independent of all view state, styling, and notification delivery.

---

# 31. Keyboard navigation

Initial proposal:

```text
Ctrl+C   cancel current operation
Ctrl+P   command palette
Tab      switch panel
Enter    activate explicitly focused action
Esc      close overlay / return
```

Exact bindings and composer newline behavior require terminal compatibility testing. Dialogs MUST NOT allow a keystroke intended for the composer to accidentally approve an operation. Destructive or security-sensitive actions MUST require deliberate focus/selection; opening an approval dialog MUST NOT preselect an affirmative action. The command palette and contextual help MUST make all core actions discoverable without memorizing shortcuts. Closing an overlay is distinct from cancelling the running task.

---

# 32. Repository structure

Illustrative target Cargo workspace, including future components. This is not a requirement to create every crate for the MVP: section 52 starts with the smallest useful boundaries and no empty ACP/MCP/team scaffolding.

```text
fluzo/
│
├── Cargo.toml
│
├── crates/
│   ├── fluzo-cli/
│   ├── fluzo-core/
│   ├── fluzo-runtime/
│   ├── fluzo-tui/
│   ├── fluzo-router/
│   ├── fluzo-harness/
│   ├── fluzo-policy/
│   ├── fluzo-agents/
│   ├── fluzo-tools/
│   ├── fluzo-mcp/
│   ├── fluzo-acp/
│   ├── fluzo-context/
│   └── fluzo-storage/
│
├── agents/
│   ├── architect.toml
│   ├── coder.toml
│   ├── reviewer.toml
│   ├── security.toml
│   └── tester.toml
│
├── skills/
│
├── teams/
│
├── examples/
│
├── docs/
│
└── tests/
```

---

# 33. Rust technology stack

Initial proposal:

| Area          | Technology                                   |
| ------------- | -------------------------------------------- |
| Language      | Rust                                         |
| Async runtime | Tokio                                        |
| TUI           | Ratatui                                      |
| Terminal      | Crossterm                                    |
| Serialization | Serde                                        |
| Configuration | TOML                                         |
| HTTP          | Reqwest                                      |
| Persistence   | SQLite                                       |
| Logging       | tracing                                      |
| Telemetry     | OpenTelemetry Rust SDK, tracing-opentelemetry, OTLP |
| IDs           | UUID                                         |
| JSON Schema   | schemars                                     |
| Git           | git CLI / git2 TBD                           |
| MCP           | MCP Rust implementation / custom adapter TBD |
| ACP           | ACP Rust SDK                                 |
| LLM APIs      | provider adapters                            |
| Testing       | cargo test                                   |

OpenTelemetry is required from the MVP. Exact crate versions, signal bridges, and the local diagnostic sink require prototype validation; other technology choices remain subject to prototype validation.

## 33.1 Platform support and portability

Ghostty and Alacritty are the required Linux reference terminals for the MVP. Visual/interaction acceptance MUST run in both, recording their versions, relevant terminal configuration, font, display backend, and hardware. The matrix MUST cover truecolor and reduced-color fallback, Unicode cell widths, keyboard shortcuts, bracketed paste, resize during streaming, clipboard behavior, focus detection, notifications, and the logo at its configured animation rates. Reduced-capability cases may be deliberately configured and MUST be identified as such. Optional notification/clipboard transports MUST use capability checks and documented fallbacks rather than assuming identical support in both terminals.

Linux is the only required and supported platform for the MVP. Required CI, release artifacts, runtime acceptance, and visual/interaction validation MUST target the documented Linux support matrix. macOS and native Windows are committed future targets, not requirements for the first release. Successful cross-compilation or operation under WSL MUST NOT be advertised as validated native Windows support.

The required MVP Linux matrix is Arch Linux and CachyOS on x86_64. ARM64 artifacts and validation are not required. Both distributions MUST support installation, native CLI/TUI execution, deterministic provider tests, session persistence/recovery, and the documented local observability workflow without access to real inference services. Other Linux distributions are not covered by the initial support promise.

Because Arch Linux and CachyOS are rolling-release distributions, release validation MUST record the test date, package/toolchain versions, runtime library requirements, and representative terminals. Support means the documented, tested up-to-date environments, not every historical package combination. Passing an Arch container test alone MUST NOT be presented as validation of CachyOS desktop/terminal behavior; distribution-specific smoke and interaction checks may use documented VMs or native machines in addition to automated CI. Test environments MUST be pinned or recorded well enough to investigate regressions without requiring the developer's personal workstation.

The distributed executable MUST target a documented portable x86_64 CPU baseline, not inherit the release builder's host-specific CPU optimizations or require a CachyOS-specific kernel. Runtime dependencies and minimum compatible library versions MUST be documented and checked on both distributions. Distribution support does not imply inclusion in official repositories or AUR publication; initial packaging requirements are defined in section 33.2.

Clipboard and desktop notification support MUST document Wayland/X11 and helper dependencies where relevant; absent optional capabilities MUST degrade visibly to terminal/in-app behavior without blocking core workflows. Linux-first does not imply support for every Linux distribution or terminal.

Core runtime and domain logic MUST avoid unnecessary platform assumptions. Filesystem paths, user configuration/data locations, shell invocation, process-tree cancellation, terminal input/rendering, clipboard access, and notification delivery MUST use portable facilities where practical and keep OS-specific behavior at their owning boundaries. Commands MUST NOT silently assume that Bash or Unix utilities exist on future platforms. Linux-specific implementations are allowed for the MVP; empty future backends or a new generic platform framework are not required merely for anticipated portability.

Promoting macOS or Windows to supported status MUST require native CI and runtime tests, installable artifacts, and platform-specific acceptance of keyboard/paste, resizing, Unicode/color rendering, permissions, paths, process termination, session recovery, and available notification/clipboard integrations. Each platform MUST also pass deterministic provider tests without real inference. Test-fixture execution commands and setup prerequisites MUST be appropriate to that platform. Portability checks may be added earlier, but MUST NOT create an implicit MVP support promise.

---

## 33.2 MVP distribution and Arch packaging

The MVP MUST provide a versioned Linux x86_64 binary archive (`.tar.gz`), documented installation from source with Cargo, and a version-controlled PKGBUILD for local package generation with `makepkg` and installation through `pacman`. Publishing to crates.io is not required for source installation. AUR publication is deferred until a later release and MUST NOT block MVP delivery.

The initial PKGBUILD MUST build from a pinned release source revision/archive rather than a moving branch, verify source integrity, use the committed Cargo lockfile, and declare build/runtime dependencies and relevant optional desktop helpers. Package metadata and licensing MUST match the chosen project identity and license. Network access for obtaining source and dependencies MUST be confined to documented preparation steps; build and check phases MUST use prepared dependencies without inference services, credentials, model downloads, or live-model tests. Mandatory deterministic checks MUST NOT be bypassed merely to generate a package.

The recipe MUST build as an unprivileged user and stage installation into the package directory rather than mutate the host during compilation. Installation hooks MUST NOT start the agent, contact model services, activate YOLO or telemetry export, or launch the observability stack. Docker and the Compose stack are optional diagnostic tooling, not required runtime dependencies of the native agent package.

Release validation MUST cover package generation in a clean Arch build environment and installation, upgrade, executable smoke tests, and removal on the documented Arch Linux and CachyOS matrix. Upgrading or removing the package MUST NOT silently delete user configuration, session databases, or diagnostic data; any irreversible application-data migration requires an explicit, documented recovery strategy. Binary archives MUST include published checksums and documented installation/runtime prerequisites. Packaging tests MUST remain independent of real inference as required by section 45.2.

---

# 34. MVP

## Local single-agent runtime

The MVP targets Arch Linux and CachyOS on x86_64, with the support and portability contract in section 33.1. ARM64 is not required. macOS and Windows support will be delivered in later releases.

The first release prioritizes a native coding agent with bounded autonomy in the user's current Git working tree, following section 21.1. It may edit workspace files and execute commands covered by existing grants; operations outside those grants require approval or are denied. It MUST preserve pre-existing user changes and MUST NOT make automatic commits or pushes. Isolated worktrees per task are a planned post-MVP capability, not a first-release requirement.

The first generative provider uses configurable OpenAI-compatible Chat Completions, including streaming and tool calls. Initial integration testing uses the existing local llama-swap server and its `flash-halogen` model ID. Base URL, model, and authentication MUST be configurable rather than hardcoded; API compatibility does not imply equivalent model quality.

Scope:

* Rust workspace
* CLI
* Ratatui TUI
* one OpenAI-compatible LLM provider, initially validated with `flash-halogen`
* filesystem tool
* shell tool
* git integration
* basic agent abstraction
* SQLite
* event bus
* configuration
* permission enforcement, cancellation, and execution limits from the first executable release
* test execution and presentation of the resulting diff and verification outcome
* OpenTelemetry traces, metrics, and correlated structured logs as defined in section 44
* local diagnostic retention and configurable OTLP export
* configurable Laya shadow observations and evaluation records

Active model-based routing, multi-agent orchestration, ACP, and MCP integrations are not required for this first release.

Success criteria:

```text
fluzo
```

can be started in a test repository, inspect files, apply a small requested change, execute the configured tests, and present the diff and test results while enforcing permissions and cancellation. The initial acceptance scenario is the Rust bug-fix workflow in section 45.1. The run MUST be diagnosable from local records and, when enabled, the OTLP destination. Laya recommendations MUST be distinguishable from actual actions and MUST NOT affect the run.

---

# 35. Post-MVP: Harness extensions

Extend the baseline harness already required by the MVP:

* richer permission policies
* additional execution budget dimensions
* retries
* configurable verification workflows
* basic loop detection

Success criteria:

The baseline guarantee that restricted operations cannot execute without policy approval remains mandatory. Retries and verification workflows MUST respect cancellation and the original execution budget.

---

# 36. Post-MVP: Router

Add:

* rule-based routing
* model-based routing
* evaluated, opt-in active routing through decision-provider adapters, extending the MVP Laya shadow adapter
* agent selection
* tool selection

Success criteria:

The runtime can automatically select different agents based on task characteristics.

---

# 37. Post-MVP: Multi-agent

Add:

* Task Graph
* parallel execution
* delegation
* agent dependencies
* shared artifacts
* agent context propagation

Success criteria:

A feature can be implemented using:

```text
architect
    ↓
coder
    ↓
tester
    ↓
reviewer
```

---

# 38. Post-MVP: ACP

Add:

* ACP client
* external agent discovery/configuration
* ACP agent lifecycle
* ACP events
* ACP permissions integration

Success criteria:

At least two external ACP-compatible agents can participate in an Fluzo task.

---

# 39. Post-MVP: MCP

Add:

* MCP client
* server configuration
* tool discovery
* tool invocation
* MCP permission enforcement

Success criteria:

An external MCP server can provide tools to Fluzo agents.

---

# 40. Post-MVP: Teams

Add:

* team definitions
* dynamic teams
* team strategies
* parallel execution
* team-level policies

---

# 41. Future roadmap

Potential future versions:

Committed post-MVP capability (release milestone TBD): isolated Git worktrees per task, usable by a single agent as well as future multi-agent workflows. The MVP MUST establish the explicit task-workspace contract in section 21.1 without implementing worktree lifecycle management yet.

Committed post-MVP platforms: macOS and native Windows, each with its own release milestone and validated support matrix. Their order of delivery remains open; Linux portability boundaries MUST be established as described in section 33.1.

## v1.0

Stable:

* TUI
* runtime
* agents
* routing
* harness
* MCP
* ACP
* multi-agent
* persistence
* replay

## v1.x

Potential:

* LSP integration
* remote agents
* remote execution
* Docker/Podman sandboxing
* advanced context engine
* agent marketplace
* plugin system

## v2.x

Potential:

* Proxmox execution backend
* Kubernetes execution backend
* distributed agent runtime
* web UI
* VS Code integration
* remote Fluzo server
* team marketplace

---

# 42. Security model

Security defaults should be conservative.

Default:

```text
Filesystem:
    workspace only

Shell:
    ask

Network:
    deny

Git commit:
    ask

Git push:
    ask

Destructive commands:
    deny/ask

Credentials:
    deny
```

The exact default policy requires validation during implementation. Approved model, decision-provider, and telemetry destinations need explicit runtime network grants; these MUST NOT grant arbitrary network access to tools. Authorizing a shell command can execute repository code and is not equivalent to operating-system sandboxing.

In the local MVP, filesystem/network restrictions apply to Fluzo-mediated native operations. An approved unsandboxed program can use the OS filesystem/network outside those APIs; a `tool_network = "deny"` setting MUST NOT be presented as a kernel-enforced firewall for that process. Workflows requiring that stronger guarantee must refuse unsandboxed execution until a suitable backend exists. The UI MUST show this distinction before the user grants shell or YOLO access.

## 42.1 No automatic HTTP redirects

All application-owned HTTP clients MUST disable automatic redirect following, including generative models, Laya, model discovery, setup probes, and OTLP export. Any 3xx response is a protocol/security outcome, not permission to resend a body or credentials to its `Location`. This applies even to a same-origin redirect; a changed endpoint requires explicit user configuration and destination consent. The agent MUST NOT override this rule, follow the redirect itself as a workaround, or silently choose another provider. Arbitrary traffic from an approved unsandboxed shell remains outside this HTTP-client guarantee.

The runtime MUST emit a structured `redirect_blocked` result with status code, operation/correlation IDs, and only a sanitized destination summary if parseable. Logs MUST omit URL credentials, sensitive path/query/fragment values, headers, and request bodies. The TUI/CLI MUST show a relevant notification and diagnostic entry. When an authorized agent interaction can continue, include the structured failure as runtime/tool context so the agent can explain it or request user intervention, but not grant itself destination authorization. If the primary model request itself was redirected, no model response is possible through that call: block the task and surface the error directly to the user. Laya/exporter failures follow their non-blocking degradation rules rather than falsely succeeding.

Tests MUST use a redirecting simulator and a second listener to assert zero requests and zero forwarded credentials/body bytes at the redirect target, covering 301/302/303/307/308, relative/absolute locations, same/cross-origin targets, and malformed or secret-bearing `Location` values. Redirects MUST NOT enter transient-request retry loops.

---

# 43. Cost control

Agent execution should expose budget controls.

## 43.1 Agreed MVP defaults

The following defaults MUST be configurable and enforced by the runtime in both normal and YOLO modes:

| Limit | Default |
| ----- | ------- |
| Agent turns per task | 30 |
| Active elapsed time per task | 20 minutes, excluding user-wait time |
| Shell command execution timeout | 120 seconds |
| Additional retries per transient provider request failure | 2 (at most 3 attempts total) |
| Automatic context compaction threshold | 80% of available input capacity |

All defaults below MUST also be adjustable in normal TUI settings and persisted in `.fluzo`; these are initial tuning values, not universal model capabilities:

| Additional limit | Initial default |
| ---------------- | --------------- |
| Effective context window | 32768-token setup suggestion, confirmed for the chosen model |
| Maximum/reserved response output | 4096 tokens, within model capabilities |
| Additional input safety reserve | Greater of 1024 tokens or 5% of the context window |
| Compaction summary output | 2048 tokens, within response capacity |
| Task token budget | 200000 input plus output tokens, including cached input and compaction |
| Tool calls per task | 100 dispatches, including verification |
| Tool result supplied to model | 64 KiB, also constrained by available input tokens |
| Captured artifact per tool call | 2 MiB combined stdout/stderr |
| Provider connect / first output / idle stream / whole request timeouts | 10 / 90 / 30 / 180 seconds |
| Laya whole request timeout | 5 seconds; no automatic retries |
| Model and pool concurrency / pool queue capacity / queue wait | 1 / 8 / 30 seconds, as detailed in section 43.3 |
| Monetary budget | Disabled unless explicitly configured with currency and price data |

Limits MUST be validated together against the selected model and task. First-output timing MUST measure actual model output or a completed response, not headers/keepalives. After output begins, meaningful model progress resets the idle timer but not the whole-request deadline. Request/queue deadlines MUST be bounded by the remaining active-task time. For eligible non-quota transient failures only, provider retry backoff defaults to 1 then 2 seconds within the remaining budget. Fluzo MUST NOT schedule waits or retries from `Retry-After` or rate-limit headers. Actual eligible retries remain subject to local slot reconciliation in section 43.3.

Before inference, input estimates plus maximum response output MUST fit the remaining token budget. Reported usage reconciles the reservation; absent usage requires a documented conservative estimate and an uncertainty indicator, not zero consumption. Monetary enforcement requires usable price data and conservative usage accounting. Tool-output readers MUST drain pipes safely after the capture cap without unbounded buffering, retaining an explicit truncation marker. No finite result limit authorizes silently deleting already retained history. Normal TUI controls MUST expose the capacity/capture tradeoff and the effective configuration snapshot.

A turn is one logical agent-model interaction, including processing its response and any resulting tool calls. A request's transport retries MUST NOT count as new logical turns, but MUST consume applicable time, token, and cost budgets. Compaction requests are accounted separately from agent turns while consuming the same task budgets and bounded request-attempt allowance. Multiple tool calls within one turn MUST remain individually observable and subject to tool/policy/time limits.

Active task time MUST use elapsed wall time, not the sum of concurrent operation durations. It includes provider/tool execution, compaction, active queueing, and retry backoff. Waiting for user input or an approval, and time while a task is stopped, MUST NOT consume active time; a task MUST NOT pause its clock while its operations continue running. Resume MUST preserve prior consumption as required by section 22.1.

The shell timeout is capped by the task's remaining active-time budget. On timeout, the runtime MUST stop waiting indefinitely, request termination according to section 21.1, retain partial output subject to capture limits, and report any uncertain termination or side effects. Extending a command timeout requires explicit user configuration or action and MUST NOT silently extend the overall task budget.

Provider retries MUST be limited to safely classified non-quota transient failures, such as temporary service errors or connection interruptions, with bounded local backoff and cancellation support. HTTP 429, explicit quota/rate-limit errors, and recognized server-capacity rejections MUST be reported as sanitized, observable failures without automatic retry, adaptive throttling, or provider fallback, even if the response includes `Retry-After`. A generic status code or SDK retry default MUST NOT override an explicit capacity rejection. Waiting for other eligible retries MUST fit the remaining task budget. Authentication errors and invalid requests MUST NOT be retried automatically. Partial responses and tool-call fragments MUST never be executed or duplicated by retrying a stream; if restarting a request cannot be done safely, the task MUST block with a clear reason. Retrying inference can still duplicate provider work or charges, which MUST not be presented as exactly-once execution. Commands with side effects MUST NOT be retried automatically.

Available input capacity means the effective context window minus reserved output tokens and protocol/safety overhead. Before a model request, reaching or exceeding the configured threshold (80% by default) MUST trigger section 16.1 compaction. The resulting context MUST fit below that threshold before continuation; otherwise the runtime MUST block instead of repeatedly compacting without progress. This threshold applies to available input capacity, not the unreserved raw context window.

Exhausting a task limit MUST block further execution, preserve history and partial changes, and expose which limit was reached and its measured consumption. Continuing requires an explicit user-authorized extension followed by resume; neither the agent nor YOLO may grant an extension automatically. Non-interactive execution MUST return promptly with a nonzero status and machine-readable `budget_exhausted` result rather than wait for input. Extensions and their scope MUST be audited without resetting previous consumption.

## 43.2 Additional budget dimensions

Model request concurrency is independent of agent/task parallelism and MUST be enforced from the single-agent MVP onward. The admission rules in section 43.3 apply even when only one native agent is active.

Budget dimensions:

```text
tokens
money
time
turns
tool calls
parallel agents
```

The canonical MVP namespaces are `[harness]`, `[models.<id>]`, `[context]`, `[decision]`, and `[capacity_pools.<id>]` as illustrated in section 27, not a competing `[budget]` configuration. Agent/team parallelism belongs to later orchestration support and MUST NOT replace model/server admission limits.

The router may use cost and latency as part of agent selection.

## 43.3 Per-process model and pool admission

Every generative or decision-model configuration MUST declare a positive integer `max_in_flight`, defaulting to 1, editable in the normal TUI and persisted in `.fluzo`. Each model MUST also belong to a named capacity pool that groups this runtime process's requests to a shared inference server or resource group. A pool has its own positive `max_in_flight`, also defaulting to 1. Multiple models configured for the same server share the conservative default pool within this instance unless the user selects another grouping. These settings are per-process ceilings, not owned physical slots or a shared server allocation.

The runtime MUST atomically admit a request only when both its local model and pool counters have capacity. These limits cover all sessions/tasks in that runtime process and every provider request path: agent turns, compaction, Laya shadow observations, authorized setup probes, and opt-in live tests. Configured aliases of the same backend model MUST share one explicit capacity identity within the runtime rather than multiply its local allowance. Eligible retries MUST re-enter admission control, and a streaming request occupies its local slot until it completes, not merely until headers or the first token arrive. No queue or semaphore wait may block input handling or cancellation.

Pool settings originate in the owning repository's `.fluzo`. Separate Fluzo processes MUST maintain independent counters without a machine-wide coordinator, server lock, normalized global pool identity, peer lookup, or shared capacity journal. Identical endpoint/pool names in two processes do not combine their limits. For example, two instances with `max_in_flight = 2` can jointly issue four requests; the user is responsible for choosing settings that their server can support. Sharing an inference endpoint MUST NOT by itself prevent a second instance from operating in another workspace. This does not change the exclusive-writer rule for the same workspace.

Default admission settings are 8 waiting requests per pool and a 30-second queue deadline for foreground requests, bounded by the task's remaining active-time budget. Queue time counts as active time and MUST be reported separately from inference time. A full queue or expired wait MUST produce a visible `capacity_exhausted` or `capacity_wait_timeout` result, not trigger an uncontrolled retry loop or silently choose another model. Scheduling MUST preserve FIFO fairness among foreground requests. Compaction is foreground work needed to continue a task, not an exemption from the limits.

Each shared pool MUST declare `foreground_reserved_slots`, default 1 and constrained to 1 through the pool's `max_in_flight`. Shadow observations MUST NOT be admitted while foreground work is queued, or when occupied/uncertain shadow slots already reach `max_in_flight - foreground_reserved_slots`. All requests still require ordinary model and total-pool capacity. With the default one-slot pool the shadow allowance is zero: observations are recorded as skipped rather than competing with the agent. A user may deliberately allocate more total capacity and leave at least one slot reserved for foreground work; a two-slot pool with one reserved slot permits at most one concurrent Laya observation. A shadow alias MUST NOT consume a foreground model's capacity identity. Lowering a limit drains existing requests and can temporarily delay foreground work; the UI MUST disclose that transition.

Cancelled queued requests MUST be removed without dispatch. On a timeout or disconnect after dispatch, the runtime MUST NOT assume that its request stopped remotely. Its local accounting marks the request/slot uncertain until completion/cancellation is confirmed or the user explicitly reconciles/resets it after a warning. This applies only to work known to that runtime or recovered from the selected repository's attempts; it is not a capacity claim visible to other Fluzo processes. No peer discovery or global reconciliation is required. Uncertainty MUST remain visible rather than silently freeing a slot and repeating an unresolved request. Cancellation APIs and server status probes are capability-dependent; Fluzo MUST NOT fabricate their availability.

Uncertain shadow requests remain charged to their shadow allowance and occupied pool count, not a blanket quarantine of all foreground capacity. Reservation prevents an observer from consuming Fluzo's entire configured foreground allocation, but cannot reserve physical GPU memory, prevent llama-swap eviction, or control unrelated clients. Concurrent residency and actual server allocations MUST be operator-confirmed, with changes/restarts and latency degradation observable. Inability to establish safe shared operation is a reason to disable/pause Laya or use an independently provisioned service, not to relax limits automatically.

Per-model and per-pool limits are local request ceilings, not discovery of physical GPU capacity. `/v1/models` and model context length do not establish the number of serving slots. The setup wizard MUST ask for the per-process limits or retain the conservative defaults, explain that multiple instances and other clients can exceed the server's aggregate capacity, and never benchmark/load-test the server automatically to infer a limit. Pool membership and local alias mappings MUST be visible in settings. Laya on the same llama-swap instance must be assigned explicitly; its shadow observations may be skipped under the conservative local pool.

Saving concurrency settings MUST follow section 26: normal TUI controls, validated positive values, and persistent `.fluzo` entries. Applying a lower limit MUST allow already admitted requests to finish while blocking new admission until usage falls below the new limit; it MUST NOT cancel them automatically. Raising a limit for the active runtime requires explicit user application, not an agent edit to configuration. Occupied, queued, uncertain, and configured slots MUST be visible per model/pool, with queue duration and saturation in bounded-cardinality metrics and traces.

Cross-instance/client/host inference coordination and external provider rate-limit management are excluded from both the MVP and the current roadmap. Provider errors remain ordinary typed outcomes available to the TUI, CLI and diagnostics. HTTP 429 and recognized capacity/quota rejections do not trigger automatic waits, retries, dynamic limit changes, rerouting or failover. A generative failure blocks/fails the attempt with a clear reason until explicit user action; optional Laya failures remain observations and may pause its local observer under section 10.1. Future support for additional providers does not add an implicit rate-limit scheduler or broker.

Deterministic HTTP-server tests MUST measure overlapping requests per runtime process and prove local model/pool limits under streaming, multiple tasks/models, compaction, eligible retries, cancelled queues, reduced limits, and uncertain termination. Tests MUST cover local alias mapping, queue bounds, Laya skips, and two independent instances in different workspaces without inference-pool arbitration. The aggregate count across those instances is not a shared-limit assertion. HTTP 429/explicit capacity-rejection fixtures MUST assert that no automatic retry, scheduled cooldown, or provider fallback occurs. Workspace-writer tests remain separate. YOLO and UI feature flags MUST NOT bypass the local admission rules.

---

# 44. Observability

## 44.1 Required signals and coverage

Observability is an MVP requirement, not a later debugging feature. The runtime MUST use OpenTelemetry for traces, metrics, and structured logs, with Rust `tracing` instrumentation bridged into the corresponding signals. The TUI and headless CLI MUST expose equivalent runtime diagnostics.

Every meaningful runtime operation MUST be observable: session lifecycle and resume, task transitions, context selection and truncation, agent turns, model requests, routing and shadow decisions, tool requests and execution, permission checks and approvals, verification, persistence failures, retries, timeouts, cancellation, and budget enforcement. This means operation coverage, not logging every keystroke or streamed token.

Spans MUST cover operation duration and record success, failure, timeout, cancellation, or denial as appropriate. Logs and domain events MUST explain state transitions and errors without treating an expected user denial as an internal failure. Client-side spans MUST exist for provider and tool calls even when the remote service has no OpenTelemetry support; remote internal spans MUST NOT be implied or fabricated.

## 44.2 Correlation and diagnosis

Each task execution attempt MUST have a root trace. Child spans MUST identify agent turns, context construction, model calls, policy checks, tool calls, verification, and Laya observations. Retries MUST be distinguishable attempts. Resumed executions start a new trace linked to the previous attempt and the same persisted task/session identifiers.

Trace context MUST propagate across Tokio tasks, runtime events, and supported outbound transports. Parallel or delayed work MUST preserve parentage or use explicit span links. Session, task, agent run, decision, and tool-call identifiers MUST correlate traces and logs with persisted domain events. Events MUST also carry a schema version, timestamp, and per-run ordering information.

Diagnostic metadata MUST include, when applicable:

* application/build version, configuration fingerprint, execution mode, and effective policy version
* provider, requested model alias, reported model identity, and available model revision
* operation and queue duration, attempts, response status, and structured error category
* input/output tokens, cached/reasoning token counts when reported, budget usage, and estimated cost provenance
* tool identity, redacted argument metadata, execution backend, exit status, and affected artifact references
* context selection metadata, size, truncation, and verification command/result references

Unavailable provider metadata MUST be marked unknown rather than fabricated. Model aliases are not immutable revisions, and unknown cost MUST NOT be reported as zero. Diagnostic reconstruction does not promise deterministic re-execution of a model or a tool.

The TUI MUST show the trace ID, operation timeline, failures, and telemetry health for a task. The CLI MUST expose equivalent identifiers and a way to retrieve local diagnostics without requiring the TUI or an external dashboard.

## 44.3 Metrics

Metrics MUST cover task outcomes and duration, provider/tool/decision latency, time to first model output, token consumption, reported or estimated cost, permission outcomes, verification failures, retries, cancellations, budget exhaustion, queue depth, and telemetry export failures/dropped records.

Metric attributes MUST have bounded cardinality. Session IDs, task IDs, trace IDs, file paths, prompts, and error text MUST NOT be metric labels. Such details belong in access-controlled traces, logs, or artifacts; exemplars may link metrics to traces when supported.

## 44.4 Laya evaluation records

Each shadow observation MUST persist a record containing:

* observation ID, trace/span IDs, source decision point, and observed state version/fingerprint
* question/schema version, candidate actions, checkpoint identity when known, and inference settings
* state size, language metadata when available, and any truncation or preprocessing applied
* typed answers, option distributions, confidence, and separate provider action scores
* recommended action, actual runtime action or absence of one, and the reason for the actual action
* latency, status, and explicit failure, timeout, cancellation, or skip reason
* later verification outcomes and optional human labels, including annotator/source and label version

Observation, actual behavior, and ground truth MUST remain separate. Agreement with the agent or a passing test is not automatically a correct label for a routing decision. Late observations MUST be linked to their original decision point without influencing subsequent actions.

Evaluation MUST support export of versioned, sanitized datasets with explicit capture consent. If input content was not captured, the record MUST state that the exact input cannot be reconstructed from its fingerprint. Sensitive replay inputs belong in a separate local artifact store, not in ordinary telemetry attributes.

Reports MUST distinguish unlabeled coverage/agreement from labeled accuracy, confusion matrices, calibration, and abstention/coverage at candidate thresholds. They MUST include sample counts, checkpoint/question versions, latency, and failure rates. Active-routing thresholds require evaluation on held-out, domain-relevant cases, including negations, Spanish/English requests, ambiguity, and failures. `action.act_probability` MUST NOT be used as an approval or safety gate.

## 44.5 Local-first storage and export

SQLite domain events remain the durable source of task history and replay; OpenTelemetry spans are not a substitute for that history. Correlation MUST work even when export is disabled, sampled, or unavailable. Events alone are not a complete OpenTelemetry signal store.

The application MUST provide a bounded local diagnostic sink and configurable OTLP export to a user-selected collector or compatible backend. No hosted telemetry account is required. External export MUST be opt-in, with explicit destination and authentication configuration. Section 44.7 defines the local reference environment; the application MUST NOT depend on its backend choices and MUST remain usable with other OTLP destinations.

Export MUST be asynchronous with bounded queues, timeouts, bounded retries, and bounded shutdown flushing. Collector failure, disk limits, or queue saturation MUST NOT indefinitely block the runtime. Telemetry degradation and dropped-record counts MUST be visible locally. Domain-state persistence failures MUST be surfaced separately and MUST NOT be silently treated as successful persistence.

Diagnostic/evaluation mode MUST use 100% trace sampling and retain all Laya observations within configured retention limits, including failed and skipped requests. Standard mode MAY use configurable sampling, but sampling MUST NOT remove mandatory domain audit events or evaluation records. Full sampling is not a guarantee of delivery; dropped data and gaps MUST be reported.

Local history and diagnostic archives MUST default to no automatic expiry, with finite admission/capture limits and explicit cleanup as defined in section 22.2. Archival file rotation MAY split files but MUST NOT silently delete retained records. Retention at an external destination is governed separately and MUST be disclosed; enabling export is not a promise of indefinite backend storage.

## 44.6 Privacy and access

Default telemetry MUST capture operation metadata, not raw prompts, source code, tool arguments/results, diffs, shell output, or model reasoning. Credentials, authorization headers, environment secrets, and sensitive URL parameters MUST never be recorded. File paths and error messages MUST be sanitized according to the effective capture policy.

Local session content required for recovery is retained under section 22.2 and MUST NOT be copied into diagnostic attributes by default. Additional diagnostic content capture MUST be explicit, scoped to a session or test run, bounded, access-controlled, and redacted before persistence/export. Credential redaction and access restrictions apply to session databases and artifacts as well as telemetry. Full model reasoning is not required. Project configuration MUST NOT silently enable diagnostic content capture or export against user-level privacy restrictions.

Remote telemetry export MUST use TLS or an explicitly trusted protected transport. Loopback collectors may use HTTP. Laya observation requests themselves send state to a configured service and MUST follow the same destination trust and data-minimization policy as model requests.

## 44.7 Local Docker Compose test environment

The project MUST provide a reproducible, optional observability environment using Docker Compose v2. The default development workflow runs the native Fluzo CLI/TUI on the host and the observability services in containers. The environment MUST NOT require Kubernetes, hosted accounts, a GPU, or containerizing the application. Existing Halogen and Laya services remain separately configured dependencies and MUST NOT be started, stopped, or reconfigured by this stack.

The reference stack consists of:

| Service | Responsibility |
| ------- | -------------- |
| OpenTelemetry Collector Contrib | Receive OTLP traces, metrics, and logs; batch and forward them through bounded pipelines |
| Tempo | Store and query traces |
| Prometheus | Scrape the Collector's application-metrics endpoint and store time series |
| Loki | Store structured logs received through its native OTLP ingestion endpoint |
| Grafana | Provide provisioned data sources, dashboards, and trace/log navigation |

The signal flow MUST be explicit:

```text
Fluzo on host -> OTLP -> Collector
                             |-- traces -> Tempo
                             |-- logs   -> Loki (OTLP HTTP)
                             |-- metrics endpoint <- Prometheus scrape

Grafana -> Tempo / Loki / Prometheus
```

Only Grafana and Collector ingestion ports MUST be published to the host, bound to `127.0.0.1` by default: Grafana on `3000`, OTLP gRPC on `4317`, and OTLP HTTP on `4318`. Ports MUST be configurable for conflicts. Backends communicate over the Compose network and MUST NOT publish host ports. Host clients use loopback OTLP endpoints; container-to-container connections use service names, not `localhost`. Application export remains an explicit opt-in even when the stack is running.

Service images MUST use pinned, mutually compatible versions, not `latest`. Compose configuration, Collector pipelines, backend configuration, Grafana provisioning, and a credential-free example environment MUST be version-controlled. Grafana authentication MUST be enabled with locally supplied credentials excluded from Git; anonymous access MUST be disabled. Configured data sources and dashboards MUST require no manual UI setup. Backend plugins MUST NOT require downloads at startup; initial image pulls require network access, but a cached stack MUST operate offline.

Persistent backend data MUST use named volumes, with backend configuration mounted read-only where supported. The stack MUST NOT mount source workspaces, application SQLite databases, credentials, or the Docker socket. Only explicitly exported telemetry crosses from the runtime into this environment.

The application's durable local history/diagnostic archive has no automatic expiry under section 22.2. The reference Compose backends are separately bounded query stores: initial configurable retention is 72 hours for traces/logs and 7 days for metrics, with a 1 GiB Prometheus retention-size target. Setup and documentation MUST explicitly disclose this distinction; Grafana is not the indefinite archive, and an aggregate local archive does not promise lossless rehydration of every backend. These query-store policies MUST be configurable through `.fluzo` and TUI settings, with explicit application/restart of the dedicated stack rather than pretending a client-only save has changed a backend. External/shared backend policies remain administrator-managed.

These retention targets are not hard disk quotas: compaction, WAL files, and in-flight data can exceed them. Before delivery, service memory limits, bounded Collector queues, container-log rotation, and disk requirements MUST be established from a smoke run. Disk usage and telemetry drops MUST be visible; strict disk ceilings require separately configured filesystem or volume quotas. Operational container logs are not a substitute for the durable Fluzo diagnostic archive.

The documented lifecycle MUST include configuration validation, startup with readiness checks, service health/log inspection, restart, and shutdown preserving data. The intended root command is `docker compose up -d --wait` after the documented one-time credential setup. Deleting volumes MUST be a separate, explicitly destructive operation, never part of routine shutdown or test execution. Readiness checks MUST use mechanisms supported by the selected images and MUST NOT assume tools such as `curl` exist inside minimal containers.

Initial provisioned dashboards MUST cover:

* task outcomes, latency, model/tool calls, token use, and permission/verification outcomes
* Laya shadow latency, failures, skips, and recommendation/action agreement, clearly distinct from labeled accuracy
* Collector/backend health, export failures, queue saturation, and telemetry drops

Trace IDs in logs MUST link to Tempo, and trace views MUST support querying related logs in Loki. Run/task/decision IDs MUST remain structured metadata rather than Loki index labels or Prometheus labels. Full Laya evaluation records remain in the runtime's local store and dataset exports; Grafana is a diagnostic view, not the ground-truth database.

Acceptance MUST include a deterministic, model-independent smoke run that emits a trace, a correlated structured log, and a metric, then verifies ingestion in all three backends and navigation from Grafana. A mock Laya response MUST produce an inspectable shadow observation without changing execution. Readiness alone is not sufficient. Tests MUST also cover a Collector outage without blocking the runtime, restoration of new-signal export with gaps reported, and data surviving an ordinary stack restart. Delivery MUST document tested Docker/Compose versions, architectures, startup time, and observed memory/disk use. Lossless delivery during outages is not implied.

---

# 45. Testing strategy

Testing layers:

```text
Unit
Integration
Protocol
Runtime
Harness
TUI
End-to-end
```

Important test areas:

* routing
* policy enforcement
* task graph execution
* agent lifecycle
* tool permissions
* loop detection
* persistence
* replay
* ACP
* MCP
* trace/log/event correlation across asynchronous work, retries, cancellation, and resume
* session reopening without provider/tool calls, explicit resume, workspace reconciliation, stale approval invalidation, and unknown outcomes after a simulated crash
* crash boundaries before tool dispatch and after side effects but before outcome persistence, without automatic command replay or silent budget reset
* OTLP export to a local test collector and diagnostic operation with export disabled
* reference Docker Compose readiness, three-signal ingestion, provisioned Grafana correlation, and persistent restart
* exporter outage, bounded buffering, retention, shutdown, and visible dropped-record counts
* secret redaction and opt-in content capture across events, artifacts, and telemetry
* Laya shadow isolation, typed response validation, timeout handling, and labeled evaluation
* deterministic context selection, scoped instructions, secret exclusions, bounded tool output, and automatic compaction success/failure through HTTP simulators
* exclusive workspace writer ownership, safe pause/reacquisition, and native path containment under traversal/link/race fixtures
* closed subprocess stdin, scoped environment injection, owned-process graceful/forced termination, and disabled implicit Git helpers
* untrusted streaming terminal content, misleading filenames, and safe replay/CLI rendering without raw control sequences
* blocked HTTP redirects with a non-contacted target listener and redacted agent/user diagnostics
* foreground slot reservation, Laya devmenu control/pause, repository-scoped storage, and cross-repository config/data isolation

A deterministic mock agent should be provided for tests.

## 45.1 Initial MVP acceptance: fix a Rust bug

The first end-to-end acceptance scenario MUST use a small, version-controlled Rust fixture repository containing a reproducible implementation bug, one failing regression test, and additional passing tests. The fixture MUST compile successfully before the fix; its initial failure MUST be an assertion exposing the intended bug, not a missing dependency, unavailable service, or toolchain error. It SHOULD require no third-party crates or network access to execute tests with the documented Rust toolchain.

The user request is to reproduce the failing test, correct the implementation without weakening the tests, and report the changes and verification results. The fixture revision, user prompt, toolchain, test command, execution profile, provider or mock-scenario version, permissions, and finite turn/time/tool-call budgets MUST be recorded in a versioned test specification before implementation is accepted. In the live-model profile, the expected patch MUST NOT be supplied to the agent as context, and equivalent correct implementations MUST be allowed. In the deterministic profile, a scripted provider supplies known responses to test execution behavior, not model problem-solving ability.

Each run MUST use a disposable copy of the fixture initialized as a Git repository, with the agent editing that copy in place. Test setup and cleanup MUST NOT reset, clean, or overwrite the developer's working repository. The toolchain and required images MUST be prepared before the run; dependency downloads are not part of the agent's task.

The acceptance workflow is:

1. Start the selected profile's local telemetry test receiver, or the reference Compose stack for the observability integration profile, and explicitly enable diagnostic-mode export for this synthetic run.
2. Launch the native agent in the fixture repository with Laya shadow mode against the deterministic HTTP provider simulators by default. Only the explicitly selected live profile uses real model services, initially `flash-halogen` and Laya on the developer's configured llama-swap server.
3. Inspect relevant files and execute the designated test command under an explicit test-command grant, recording the expected initial assertion failure before any edit.
4. Modify the implementation within workspace permissions without changing or disabling the existing tests, relaxing assertions, or bypassing verification through build/test configuration changes.
5. Rerun the designated suite and expose the final diff, test outcomes, task status, and trace ID through the headless CLI; a separate TUI check MUST verify their visibility in the interface.
6. Independently rerun the suite from the test harness and verify that existing tests/configuration were not weakened and that no unrelated changes were introduced.

Success requires the original failure to be reproduced, all final tests to pass, and the implementation change to satisfy the fixture's expected behavior. An agent's success message alone is insufficient. No automatic staging, commits, or pushes are allowed. Budget exhaustion, an unavailable model, a denied required operation, or incomplete verification MUST be reported distinctly and MUST NOT count as a successful repair.

The persisted event history and local diagnostics MUST correlate with the exported trace and logs for inspection, model calls, tool calls, policy outcomes, the initial test failure, edits, and final verification. Metrics MUST be ingested without using task IDs as labels. Laya observations MUST be associated with their original decision points and actual actions, with failures or skips visible. A successful Laya response is not required for the repair to succeed, and its recommendations MUST NOT affect execution.

Deterministic mock-agent tests MUST separately exercise a denied command, cancellation with partial edits, pre-existing user changes, and unavailable Laya/Collector services. These safety checks MUST NOT depend on a live model voluntarily producing the desired failure case. The headless runtime MUST support the same fixture workflow; TUI visibility is an additional acceptance check, not a second implementation of execution logic.

The deterministic scenario validates runtime and protocol integration, not model quality. The optional live-model variant also does not establish a statistical model success rate by itself. Reports MUST include every attempted run and its outcome, profile, fixture/model or mock-scenario/configuration identity, duration, and token usage provenance; synthetic usage MUST NOT be presented as real inference consumption. Failed attempts MUST NOT be hidden by reporting only a successful retry. Repeated live quality evaluation and a model success-rate threshold remain separate from mandatory CI/release checks.

## 45.2 Provider simulation and test profiles

No required CI, pull-request, fork, build, packaging, or release-validation workflow may depend on access to a real llama-swap deployment, model weights, a GPU, private infrastructure, provider credentials, or paid inference. Developers MUST be able to build, run mandatory tests, and generate local release artifacts without those resources. Registry access for initial dependency/image downloads and credentials for publishing artifacts are separate prerequisites, not inference requirements; fully air-gapped dependency bootstrapping is not implied.

The project MUST provide an HTTP test server simulating the protocol boundary exposed through llama-swap. It MUST NOT require installing or starting llama-swap or any inference backend. Base URLs MUST be injectable, and the simulator MUST bind to loopback with isolated ports and state per test run, allowing concurrent tests without contacting a developer's configured services.

The simulator MUST cover the consumed API subset:

* model discovery when used by the client, plus non-streaming and streaming `/v1/chat/completions`
* SSE framing, fragmented tool-call arguments, finish reasons, usage metadata, and stream completion
* multi-turn tool-call/result exchanges that validate request structure and expected scenario transitions
* Laya's typed `/v1/systemone` requests and the configured llama-swap-style `/upstream/laya/v1/systemone` route
* controlled HTTP errors, malformed responses, invalid typed answers, slow responses, disconnects, cancellation, and unavailable services

Versioned synthetic scenarios MUST drive responses deterministically. Unexpected requests MUST fail with a useful diagnostic rather than returning unconditional success. The simulator MUST NOT edit fixture files or run tools itself: the real native agent, provider adapters, harness, policies, tools, persistence, and telemetry MUST perform those actions. Existing `MockAgent` unit tests remain complementary and MUST NOT replace HTTP-boundary acceptance coverage. The simulator tests the client-facing contract, not llama-swap's process swapping or actual model fidelity.

The documented test profiles MUST be:

| Profile | Dependencies | Purpose and gating |
| ------- | ------------ | ------------------ |
| Deterministic E2E (default) | Local HTTP simulators, telemetry test receiver, Rust toolchain | Mandatory CI/release checks; no real inference or Docker required |
| Observability integration | Simulators plus the reference Docker Compose stack | Verify three-signal storage, dashboards, correlation, and restart behavior in a dedicated Docker-capable job; no real inference |
| Live-model E2E (opt-in) | Explicitly configured model/decision endpoints and finite budgets | Developer or manually authorized evaluation; never required to build, package, or pass standard CI |

Default tests MUST ignore real provider URLs and credentials from user/project configuration and MUST NOT probe for available inference services. CI MUST restrict provider-test traffic to the local fixtures; mocks MUST never fall back to cloud or local real models. Standard pull-request and fork workflows MUST NOT receive inference secrets. Live tests MUST require an explicit profile selection and target configuration and MUST NOT be enabled merely because a secret or endpoint is present.

Not selecting the live profile MUST yield an explicit `not_run` or equivalent report entry, not a successful live-validation claim. An explicitly selected live run MUST report connection errors, budget exhaustion, and assertion failures accurately and return a failing result; it MUST NOT silently switch to a simulator. A developer without server access runs the default deterministic profile instead. Successful deterministic checks MUST permit version generation with live tests recorded as not run; bypassing live E2E MUST NOT bypass required deterministic or applicable observability checks.

The implementation MUST document exact commands for each profile and local release-artifact generation, with unambiguous names and example configuration containing no private endpoints or secrets. A clean-checkout/fork validation MUST prove that the mandatory checks and local packaging complete without any real inference requests. Live results, when available, MUST be reported separately from deterministic CI results.

---

# 46. Developer experience

The project should make it easy to add:

### New agent

```text
agents/my-agent.toml
```

### New skill

```text
skills/my-skill/
```

### New team

```text
teams/my-team.toml
```

### New policy

Implement:

```rust
trait Policy
```

### New execution backend

Implement:

```rust
trait ExecutionBackend
```

### New router

Implement:

```rust
trait Router
```

---

# 47. Extensibility architecture

The following interfaces should remain stable:

```rust
Agent
Router
Harness
Policy
Tool
ExecutionBackend
ContextProvider
Storage
```

This should allow replacing implementations independently.

---

# 48. Example complete workflow

User:

```text
"Implement OAuth login with Google and add tests."
```

Runtime:

```text
             USER
              │
              ▼
           ROUTER
              │
              ▼
          ARCHITECT
              │
              ▼
        TASK GRAPH
              │
       ┌──────┴──────┐
       ▼             ▼
    CODER         SECURITY
       │             │
       └──────┬──────┘
              ▼
           TESTER
              │
              ▼
          REVIEWER
```

During execution:

```text
Coder → filesystem.read
       → filesystem.write
       → shell.test

Policy → allow

Tester → shell.test

Tests fail

Router → replan

Coder → fix

Tests pass

Reviewer → approve
```

Final result:

```text
Task completed
12 files changed
127 tests passed
1 security issue fixed
$0.83 estimated cost
```

---

# 49. Success metrics

## 49.1 Proposed MVP measurement contract

The following makes the initial targets measurable. The first visual prototype MUST establish a versioned reference environment/profile and obtain product-owner review of these proposed gates. A failed target requires optimization or an explicitly recorded requirement change; it MUST NOT be quietly redefined as a different statistic or workload. Before implementation measurements exist, these are targets, not performance claims.

| Metric | Proposed MVP gate | Definition |
| ------ | ----------------- | ---------- |
| Warm startup | p95 < 100 ms | External launch/exec to first useful frame written and input loop ready, with valid trusted config and current DB schema |
| Idle process memory | Maximum observed RSS < 100 MB (100000000 bytes) | Fluzo process only during a 30-second quiescent measurement window; no active animation or inference |
| TUI input response | p95 < 50 ms; p99 < 100 ms | Input delivered to the PTY until the corresponding visible application update is written, under the streaming workload below |
| Runtime event delivery | p95 < 10 ms | Monotonic publication time to acceptance by each required local consumer, excluding subsequent terminal display/GPU/network time |
| Animation work at 60 FPS target | p95 frame compose/write duration < 16.7 ms | Application render work, with achieved redraw cadence and skipped frames reported separately from display FPS |
| Runtime stability | No unexpected panic, process crash, or unrecovered hang in at least 1000 deterministic attempts | Report the observed rate; a one-sided 95% population lower bound > 99% requires separately justified sampling assumptions |
| Recorded-event replay | 100% of retained committed events accounted for | Stable ordering/identity and reconstructed state; explicit redaction/gaps/unknown outcomes, no external calls or tool re-execution |

The startup profile MUST launch a fresh process on each sample after dependencies/assets and OS caches are warm; it MUST NOT reuse a running application to claim startup time. At least 100 warm starts are required. First-ever setup, migrations, and cold-cache startup MUST be reported separately with their conditions and sample counts; no universal cold-start gate is claimed until a reproducible baseline is approved. A blank/splash frame does not count as readiness.

The process-memory target excludes model servers, Collector/backends, and the terminal emulator, which MUST have separate resource measurements rather than vanish from the report. MB and MiB MUST not be interchanged. Both a small session and the large-history fixture MUST be measured after loading the visible view; paginated history/artifact access MUST prevent retained disk size from becoming resident process size. Peak RSS during active rendering/export MUST also be reported, not mislabeled as idle RSS.

## 49.2 Reproducible profiles and sample policy

Profiles MUST pin the release build, commit, Rust/toolchain and crate lockfile, OS/kernel, CPU/RAM, terminal version/font/configuration, display backend, viewport, effective `.fluzo`, fixture seed, and telemetry settings. Ghostty and Alacritty MUST each have a documented run on the Arch/CachyOS support matrix; performance acceptance applies to the recorded reference hardware, not every possible user machine. A missing environment or measurement MUST be marked unverified, not passed.

The synthetic streaming profile MUST generate 50 text deltas and 10 tool/status events per second for at least 60 seconds, without real inference. It MUST include scrolling away from live output, typing/paste, a permission dialog, notifications, compaction/capacity states, resize, and cancellation. Input/event latency reporting needs at least 1000 timed samples per reference profile, with p50/p95/p99, maximum, sample count, and the percentile calculation method recorded. The UI contract tests MUST ensure that activity during measurements does not steal input or auto-approve actions.

Profiles MUST cover 80x24, 120x40, and 160x50 cell layouts at 60, 30, 15, and 0 animation FPS plus reduced-motion mode. The 60 FPS default is the primary performance gate; lower-rate runs validate fallback and quantify the CPU/write-volume tradeoff. Application flush/redraw timestamps MUST not be described as physical display latency. Terminal recordings and visual review complement application measurements, especially for tearing/flicker and color/glyph behavior. CPU time, renderer overruns, output bytes, and idle redraw activity MUST be reported; an idle logo MUST not run a periodic animation loop.

The generated large-history fixture MUST contain at least 10000 messages, 100000 events, and 256 MiB of permitted artifacts across multiple tasks, with an explicit seed and manifest. It MUST not contain secrets or be checked into Git as a large binary database. Tests MUST browse old tasks, open diffs, return to live activity, and replay bounded pages without eagerly loading the whole archive. Quota/full-disk tests may use lower configured limits and injected failures instead of filling a developer's real disk.

Measurements MUST distinguish export-disabled, local diagnostic capture, and local-Collector-enabled profiles. Record collector health, sampling, queues, drops, and actual capture settings. Fault profiles MUST simulate slow/unavailable export and prove responsiveness/cancellation and bounded buffering; admitted loss remains visible. Performance timing gates belong on controlled runners or documented release-validation machines, not noisy shared CI timing assertions. Ordinary PR/fork CI still requires deterministic behavior tests with a controllable clock and no real models.

## 49.3 Reliability versus model quality

For runtime stability, all started simulator-driven attempts count, including controlled task failure, permission denial, cancellation, and budget exhaustion: these are valid handled outcomes, not runtime crashes. Unexpected process death, panic, lost terminal ownership, or inability to complete a required cancellation/timeout transition within the test's documented deadline is a stability failure. Deliberately injected process kills for recovery tests MUST be reported in a separate cohort; they are neither hidden failures nor added successes. Retries MUST remain visible as separate attempts. Zero crashes in 1000 attempts gives a one-sided 95% lower bound of approximately 99.70% for that test population; it does not establish field reliability or coding accuracy. Any known reproducible crash/regression blocks release even if an aggregate percentage would otherwise pass.

That binomial calculation is conditional on independently sampled representative scenarios from a documented population. Repeating an identical deterministic trace or retrying a failed scenario MUST NOT inflate the number of independent statistical samples. If those assumptions are not established, report the suite's observed result and mark population reliability unestablished; the mandatory zero-unhandled-failure regression gate still applies. Publish generator/seeds, qualifying sample count, exclusions, and calculation method alongside any confidence bound.

Successful repair rate is a separate live-model metric: only independently verified tasks count as repaired, with all attempted tasks, model/config versions, failures, cost/usage provenance, and confidence intervals reported. Optional live runs MUST NOT become a standard CI/package prerequisite. Laya evaluation requires labeled domain cases and per-question accuracy/confusion/calibration with sample counts; agreement with agent behavior or successful API connectivity is not ground truth. No active-routing accuracy gate is claimed before that baseline exists.

The earlier sub-second routing aspiration is a future warm-provider evaluation target, not an MVP live-service CI gate. Report queue delay, transport/inference duration, cold model load/swap time, and time to first output separately. Compare Laya on/off on an operator-authorized workload to expose shared-resource contention; neither slot reservations nor asynchronous calls establish GPU isolation. Trace/audit coverage, safety tests, and data-integrity checks are independent mandatory gates and MUST never be averaged away by latency or task-success metrics.

---

# 50. Open architectural questions

Resolved MVP decisions are recorded below; remaining questions MUST remain explicit during design.

## Q1 — Laya vs Jev

MVP decision: consume an external Laya service through its typed HTTP API in optional shadow mode. Do not embed its Python runtime in the Rust process. Keep the decision-provider abstraction replaceable; Jev compatibility and active routing are later capabilities requiring separate validation.

---

## Q2 — ACP vs native agents

MVP decision: implement the native coding agent first, with bounded autonomy and an OpenAI-compatible generative provider. ACP interoperability remains on the later roadmap.

---

## Q3 — MCP ownership

Should MCP servers be:

* globally configured?
* project configured?
* agent configured?
* dynamically granted?

---

## Q4 — Context

MVP decision: deterministic initial context with policy-controlled file discovery by the native agent, explicit skills, and automatic model-generated history compaction as defined in section 16.1. Summaries are non-authoritative; runtime state remains independent. Laya-based context selection, automatic skill discovery, LSP, and semantic memory remain outside the initial scope.

---

## Q5 — Agent communication

Should agents communicate:

```text
directly
```

or exclusively through:

```text
Runtime → Task Graph → Events
```

The latter is preferred initially.

---

## Q6 — Shared workspace

Decided: use the current working tree for the single-agent MVP and add isolated Git worktrees per task in a future release, following section 21.1.

Still open for multi-agent execution: whether agents collaborating on one task share its worktree, how concurrent writers are coordinated, and how dependent task worktrees exchange changes. These decisions MUST precede concurrent editing support.

---

## Q7 — Git strategy

MVP decision: remain in the current working tree and branch without automatic staging, stashing, commits, or pushes. Git mutations require explicit user approval.

Future decision: isolated worktrees are task-scoped, not necessarily agent-scoped. Branch naming, base revision, review/integration workflow, conflict handling, and cleanup remain to be defined. No automatic merge into the user's branch is implied.

---

## Q8 — Memory

MVP decision: retain repository-local history and compaction artifacts in `.fluzodrive/`, with bounded incremental retrieval for task inspection and explicit context assembly. Do not add semantic retrieval, an autonomous memory agent, or cross-repository memory to the MVP.

Future research proposal: evaluate a skill/MCP-accessible project memory in a repository `memory/` directory, initially considering SQLite for decisions and salient recent history. Compare that baseline with graph storage for entity/dependency relationships and vector retrieval for semantic similarity; no backend is selected yet. Runtime/session storage and curated long-term memory are distinct products and MUST NOT be conflated.

The evaluation MUST cover provenance/source links, timestamps and workspace revisions, obsolete or conflicting decisions, correction/deletion/export, relevance and retrieval latency on representative tasks, storage/migration cost, and multilingual retrieval. Embeddings or memory summarization may introduce inference and privacy costs and MUST use the same destination consent, budgets, and model admission as other requests. Remembered text is untrusted context, never an authorization source. Generated databases/indexes MUST remain untracked and protected; explicitly curated, non-sensitive text may be versioned only by user choice. Exact layout, schema, skill/MCP contract, and backend require a later reviewed design and deterministic fixtures before implementation.

---

## Q9 — Remote execution

Should the `ExecutionBackend` abstraction be introduced in the MVP even if only `LocalBackend` exists?

Preferred answer: **yes**, to avoid coupling the runtime to local execution.

---

# 51. Architectural constraints

The following constraints should be treated as foundational:

1. TUI must not contain business logic.
2. Runtime must not depend on TUI.
3. Agent implementations must not directly manipulate global state.
4. Policies must be evaluated before privileged operations.
5. Events must be serializable.
6. Agent state must be observable.
7. External agents must be abstracted behind a common interface.
8. MCP must remain independent from individual agents.
9. Router implementations must be replaceable.
10. Execution backends must be replaceable.

---

# 52. Initial implementation order

Implementation MUST proceed through small demonstrable milestones. TUI design review and deterministic test infrastructure precede reliance on real inference. No milestone may execute workspace-mutating tools without the policy, persistence, and cancellation checks required for those tools.

| Milestone | Deliverable and exit check |
| --------- | ------------------------- |
| 1. Foundation | Minimal Cargo workspace, MIT metadata, versioned `.fluzo` schema/defaults, runtime events and correlation IDs, and a deterministic scenario driver |
| 2. Visual prototype | Early Crush-inspired TUI, welcome/settings, 60 FPS logo, notifications and devmenu; user-reviewed synthetic scenarios, terminal snapshots and input/resize tests |
| 3. Diagnostics and storage | SQLite session/audit state, bounded no-expiry local archives, explicit cleanup, OTLP signals, and Compose with a model-independent three-signal smoke test |
| 4. Safe execution | Workspace-aware tools, normal/YOLO permissions, cancellation/recovery, persisted budget accounting, and per-model/shared-pool admission with HTTP-simulated concurrency tests |
| 5. Native agent | OpenAI-compatible streaming/tool calls, deterministic context, compaction, optional Laya shadow adapter, and full Rust bug-fix acceptance using simulators |
| 6. Integration and release | Complete TUI/runtime integration, settings-to-file and resume checks, Arch/CachyOS validation, archive/PKGBUILD delivery and local release artifacts; live inference is optional and separately reported |

Each milestone MUST add focused regression tests and observability for the behavior it introduces. Synthetic early UI events MUST remain visibly separate from real task execution and converge on the same runtime event contracts rather than creating a second execution engine. The settings registry MUST drive defaults, validation, serialization, and TUI controls to prevent UI/file/runtime drift. Exact internal crate partitioning may remain minimal until implementation justifies additional boundaries.

After MVP acceptance, plan isolated worktrees, evaluated active routing, task graphs/teams, ACP/MCP, and other execution backends as separate deliveries. macOS and native Windows require their own validation gates. Their exact order and dates remain open; none is a prerequisite for the agreed Linux MVP.

---

# 53. Definition of Done — MVP

The MVP is complete when:

* [ ] `fluzo` starts successfully in a Git repository
* [ ] TUI renders correctly
* [ ] approved reference performance profiles report startup/input/render/event percentiles, idle/peak memory, large-history behavior, and stability sample assumptions without substituting live inference for mandatory CI tests
* [ ] English UI/help/diagnostics and terminal interaction tests pass in both Ghostty and Alacritty, with versions and capability-dependent fallbacks documented
* [ ] the opt-in Developer Menu supports reversible UI tuning and an explicit Laya shadow switch that preserves consent/capacity rules; demo/test modes never call real providers
* [ ] the original pixel-art logo passes visual review with runtime-driven animation targeting 60 FPS, configurable lower rates, static/reduced-motion modes, and measured responsiveness under streaming
* [ ] the Arch Linux and CachyOS x86_64 support matrix, tested package versions/dates, CPU baseline, and installation requirements are documented; runtime, TUI, and packaging checks pass on both distributions without real inference
* [ ] a versioned x86_64 binary archive with checksums, Cargo source-install instructions, and a source-based PKGBUILD are provided without requiring AUR publication
* [ ] clean package builds and install/upgrade/removal smoke tests pass without inference access and preserve user configuration and session data
* [ ] the agreed MVP surfaces pass the deterministic visual/interaction demo and explicit product-owner review against the Crush reference
* [ ] TUI snapshots and pseudo-terminal tests cover supported sizes, streaming, focus, notifications, safe approvals, paste, resize, and cancellation
* [ ] themes, color fallbacks, reduced motion, and persistent normal/YOLO status remain readable without special fonts or Grafana
* [ ] user can submit a coding task
* [ ] agent can inspect files
* [ ] agent can modify files
* [ ] agent can execute tests
* [ ] agent can use Git
* [ ] shell execution is policy controlled
* [ ] normal-mode grants enforce one-time consumption, task scope, expiry, revocation, and explicit denials
* [ ] non-interactive approval requirements return promptly without dispatch, with distinct machine-readable permission outcomes
* [ ] explicit session YOLO removes authorization prompts while preserving denials, workspace/version checks, budgets, and cancellation
* [ ] YOLO activation/deactivation and automatic authorizations are visible and audited, and recovery or project configuration cannot enable it automatically
* [ ] sessions persist in SQLite
* [ ] repository-local `.fluzodrive/` is excluded from Git and agent context before persistence, with separate user-local authentication and no inherited global runtime configuration
* [ ] quotas and cleanup are repository-scoped; tests show one repository cannot silently reconfigure, purge, or inherit another repository's history or limits
* [ ] reopening a session or replaying events performs no agent/provider/tool execution; continuation requires explicit user action
* [ ] recovery distinguishes interrupted attempts and unknown operation outcomes, revalidates workspace state, and does not replay uncertain operations automatically
* [ ] resumed attempts link to prior traces, preserve known budget usage, and do not reuse pending operation approvals
* [ ] runtime events are persisted
* [ ] agent execution can be cancelled
* [ ] task results are visible in the TUI
* [ ] the Tasks menu supports read-only inspection, ordered user interventions, graceful cancellation, and confirmed force stop of owned local work without releasing uncertain ownership or slots
* [ ] configuration is loaded from project files
* [ ] welcome/setup writes a versioned `.fluzo` TOML file, and a valid existing file skips initialization even if inference is unavailable
* [ ] normal TUI settings persist limits, model/pool capacity, and devmenu preference to `.fluzo`, with round-trip, write-conflict, failure, and current-task application tests
* [ ] per-process model and pool limits are editable in the TUI, saved in `.fluzo`, and enforced across that runtime's provider paths with defaults of one; independent instances do not coordinate inference capacity
* [ ] concurrency tests prove local limits, queues, alias sharing, Laya skips and uncertain-request handling; rejection tests prove no automatic HTTP 429/capacity recovery or provider fallback
* [ ] runtime limits default to 30 turns, 20 minutes active time, 120 seconds per shell command, and at most two transient-provider retries
* [ ] deterministic tests cover user-wait time exclusion, resume accounting, shell timeout, retry classification, and budget exhaustion in normal and YOLO modes
* [ ] compaction triggers at 80% of reserved-input capacity, with boundary tests and safe blocking when compaction cannot make room
* [ ] automatic compaction preserves retained history and protocol-valid context, with observable source-linked summary artifacts and no change to authorization state
* [ ] HTTP-simulated compaction tests verify request sizing, bounded attempts, budget accounting, safe blocking on failure, cancellation, and recovery
* [ ] tests cover core runtime behaviour
* [ ] a deterministic mock agent exists
* [ ] the runtime can execute without the TUI
* [ ] the native agent passes the Rust bug-fix acceptance scenario through the deterministic HTTP provider simulators, exercising the real native agent and tools
* [ ] standard CI and local release-artifact generation pass without inference credentials, model weights, private endpoints, or real inference requests
* [ ] live-model E2E is explicitly opt-in, reports unavailability/failures without silent mock fallback, and can be omitted without blocking standard release validation
* [ ] the fixture reproduces the expected failure before editing and passes independent final verification without weakened tests or unrelated changes
* [ ] bounded autonomy preserves user changes and requires approval outside existing grants
* [ ] task tools, context, policies, and verification use the explicitly assigned workspace root, tested independently of the startup directory
* [ ] edits appear in the current working tree without automatic branch, worktree, stash, or staging operations
* [ ] tests cover staged/unstaged/untracked user changes, native edit approval, and invalidation after an external file change
* [ ] cancellation stops new actions, reports unconfirmed termination, and preserves partial edits without automatic rollback
* [ ] workspace writer ownership is exclusive across local sessions/processes; native path confinement tests cover traversal, links, races, and protected paths
* [ ] subprocess tests prove closed stdin, explicit environment injection, absent inherited provider secrets, and no unapproved Git helper execution
* [ ] untrusted display tests prevent terminal-control injection and approval spoofing across live output, history, replay, and CLI views
* [ ] all application HTTP clients reject redirects without contacting the target, and produce sanitized, actionable redirect-blocked outcomes
* [ ] traces, metrics, and correlated logs are visible through a local OTLP test collector
* [ ] the reference Docker Compose stack starts with provisioned dashboards and passes the model-independent three-signal smoke test
* [ ] all required runtime operations have coverage in a deterministic mock-agent diagnostic run
* [ ] trace/task IDs connect TUI and CLI diagnostics to persisted events across retries and cancellation
* [ ] local diagnostics work without a collector; exporter failure does not block task completion
* [ ] local no-expiry retention, finite admission/capture limits, explicit history/telemetry cleanup, redaction, and telemetry-loss reporting are tested
* [ ] deletion tests cover dry-run, active-session protection, shared artifacts, partial failure, quiesced export buffers, and accurate reporting of untouched remote stores
* [ ] Laya recommendations, actual actions, and human labels can be inspected independently
* [ ] Laya results/failures never authorize or dispatch agent actions; disabling and timeouts preserve foreground slot reservations, with shared-hardware latency effects reported rather than denied
* [ ] evaluation records can be exported as a versioned, sanitized dataset with labeled and unlabeled results distinguished

---

# 54. Definition of Done — Multi-agent

* [ ] Task Graph implemented
* [ ] multiple agents can run concurrently
* [ ] task dependencies work
* [ ] agents can delegate
* [ ] context can be transferred
* [ ] failures propagate correctly
* [ ] cancellation works
* [ ] policies apply independently to each agent
* [ ] routing decisions are persisted
* [ ] complete execution can be replayed

---

# 55. Definition of Done — Fluzo 1.0

Fluzo 1.0 should provide:

```text
              ┌─────────────────┐
              │      Fluzo      │
              └────────┬────────┘
                       │
              ┌────────▼────────┐
              │      TUI        │
              └────────┬────────┘
                       │
        ┌──────────────┼──────────────┐
        ▼              ▼              ▼
     Router         Harness        Context
        │              │              │
        └──────────────┼──────────────┘
                       ▼
                  Task Graph
                       │
          ┌────────────┼────────────┐
          ▼            ▼            ▼
       Native         ACP          ACP
       Agents        Agents       Agents
          │            │            │
          └────────────┼────────────┘
                       ▼
                      MCP
                       │
                       ▼
                   Execution
                       │
             ┌─────────┴─────────┐
             ▼                   ▼
           Local             Remote
```

The result should feel like:

> **Crush's simplicity and terminal UX + a programmable agent runtime + configurable harness + intelligent routing + multi-agent orchestration.**

---

# 56. Long-term vision

Fluzo should eventually become a **development control plane for AI agents**.

A developer should be able to say:

```text
"Build this feature."
```

and Fluzo should determine:

```text
What needs to happen?
        ↓
Which agents are needed?
        ↓
Which tools are needed?
        ↓
Where should they execute?
        ↓
What permissions do they need?
        ↓
What context should they receive?
        ↓
Can tasks run in parallel?
        ↓
How should results be verified?
        ↓
Does another agent need to review them?
        ↓
Is human approval required?
```

The human remains the final authority, while Fluzo manages the complexity of coordinating the underlying development agents.

---

# 57. Working definition

**Fluzo is not an AI coding assistant.**

It is:

> **A programmable, local-first runtime for orchestrating AI agents that build software.**

The TUI is the interface.

The Router is the brain.

The Harness is the control system.

The Task Graph is the execution model.

MCP is the tool layer.

ACP is the agent interoperability layer.

The Execution Backend is the compute layer.

And Rust is the runtime foundation.

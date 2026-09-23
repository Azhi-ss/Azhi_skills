---
name: orca-ticket-loop
description: >-
  Continuous autonomous ticket development in separate Pi terminals: launch even the
  first ticket in a fresh context, implement one ticket per context with TDD and
  self-repair, then hand off the next eligible ticket or resume the same ticket in
  a fresh Pi. Use for ticket loops, continuous development, next ticket, ticket
  workflow, 连续开发 or 一票一上下文. Never run concurrent writers in one worktree.
metadata:
  version: "2.0"
---

# Orca Ticket Loop

One implementation context works on **one ticket only**. Every ticket, including the
first, starts in a fresh Pi terminal in the active Orca worktree. One ticket may span
multiple contexts through explicit same-ticket continuation. At most one implementation
writer owns that worktree at a time.

This is a cooperative handoff protocol, not a daemon. It cannot wake itself after every
process has crashed. Do not promise unattended crash recovery without an independently
authorized external wake mechanism.

## 1. Launcher versus worker

**Launcher:** a user invoking this skill in a planning/supervisor session starts the loop.
Inspect the tracker and worktree, choose the first eligible ticket, open a new Pi terminal,
send a compact dispatch, verify delivery, report the handle, then stop. Do not claim or
implement the first ticket in this existing context. Do not launch a duplicate if a worker
already owns the worktree; report its handle instead.

**Worker:** a fresh context explicitly dispatched for a ticket runs `/implement` for that
ticket under this protocol. It repairs ordinary engineering failures autonomously. It may
finish, continue the same ticket in a fresh context, or park a blocked ticket and dispatch
an independent eligible one when the worktree is safe. It never implements a second ticket.

Read this skill from disk at each new worker start and before a handoff. Dispatch prompts
reference this protocol rather than copying its entire text. An already-running worker is
not automatically upgraded by a file edit; do not interrupt it or silently change its
active instructions. A conflict with an explicit older dispatch restriction needs a
supervisor instruction at a safe boundary, not an assumed override.

## 2. Pre-flight and ownership

Before any implementation write:

1. Verify `gh` works. Transient failures may be retried as described below. If tracker
   access remains unavailable, do not edit code or guess eligibility.
2. Read the ticket body and **all comments**, parent spec, relevant `CONTEXT.md` and ADRs.
   Require state open, `ready-for-agent`, nonempty acceptance criteria and a declared
   parent spec. Verify both textual and native blocking edges where supported.
3. Check prior stop/decision records. Already-approved decisions are reused, not asked
   again. A resolved blocker needs recorded evidence; absence of a later comment is not
   resolution. A malformed ticket or unresolved material decision is a ticket-local block.
4. Inspect the active worktree and terminal inventory. Record starting commit, tracked
   differences and untracked paths, including a bounded inventory under dirty directories.
   Identify known baseline changes; do not classify every dirty tree as unexplained.
5. Check ownership. A different GitHub assignee must not be displaced. The same login is
   **not** proof of the same worker: inspect the latest ownership/handoff comment and Orca
   terminal. Never start another implementation while an existing owner may still write.
6. For a new ticket, the first ticket-work write is
   `gh issue edit <n> --add-assignee @me`; re-read and verify sole assignee. Then comment
   the owner terminal handle, starting commit, known baseline, and intended ticket scope.
   Re-read ownership before editing. Assignment/comments are not an atomic multi-agent
   lock: this protocol assumes one serialized launcher; competing ownership is a global
   safety block.

A launcher may write a reservation/handoff record naming a newly created terminal before
sending its prompt; this is not a claim to implement. A quality/block report may be written
without claiming an ineligible ticket. Neither exception authorizes repository edits.

For same-ticket continuation, retain the current login assignment and require an explicit
handoff to this terminal. Verify the previous worker relinquished write ownership. Record
acceptance of the handoff before editing; do not unassign/reassign just to manufacture a
new claim. A stale same-login assignment without handoff or evidence the worker stopped
requires investigation, not stealing.

## 3. Default autonomy and decision boundaries

**Decide and execute without asking:** internal module/function organization, naming,
minimal implementation choices, test data within the agreed test seam, ordinary bug fixes,
review fixes, supported tool usage, and reversible local environment repair within the
existing permission/dependency policy. First inspect existing code and reuse it. Record
important choices when later contexts need them.

**Ask only for material unresolved decisions:** changes to business meaning, public data
contracts or compatibility, quality/release gates, paid calls or budgets, access scope,
destructive operations, or conflicting acceptance requirements whose resolution changes
observable results. Repository instructions and explicit approval gates still apply.

Before asking, search the spec, ADRs, comments and actual callers. Choose a conservative,
reversible implementation if it satisfies every approved requirement. Do not invent a new
approval gate for routine implementation details. Persist explicit user approval in the
tracker (or the repository's decision record) with its scope; do not re-ask after a handoff.
Do not mark an ambiguous silence as approval or edit acceptance criteria to make tests pass.

## 4. Implement, verify, self-repair

Use TDD at the agreed public seams: failing behavioral test, smallest implementation,
green. Expected TDD red is **not a blocker**. Preserve unrelated changes and historical data.

Discover gates from this repository's instructions, scripts and CI; do not use another
project's Bun commands as defaults. Run focused tests while implementing, relevant type or
static checks, the full applicable suite at completion, and `git diff --check` on the ticket
changes. If a gate does not exist, report not configured rather than inventing a passing
result. Run `/code-review` for Standards and Spec using the fixed point before the ticket's
first changes (including across continuation contexts). Review delegation still follows
applicable user/project authorization.

A test failure, type error, lint finding, review finding or command error triggers:

1. Inspect evidence, reproduce and identify the root cause.
2. Make the smallest permitted correction.
3. Re-run the failing check and relevant regressions.
4. Continue while there is measurable progress; log hypotheses/results when handing off.

After **three consecutive repair cycles with no new evidence or improvement on the same
failure**, escalate or continue in a fresh context with a concrete new hypothesis. Do not
reset this history on handoff. Three cycles is not a quota on successful fixes. Never delete
meaningful tests, weaken quality gates, hide failures, silently skip required checks, or
broaden scope merely to turn green. Pre-existing failures must be evidenced separately;
required gates remain unsatisfied unless the authorized policy explicitly permits them.

For a clearly transient read/network/tool failure, allow at most two retries after the
initial attempt within applicable time/cost limits. Authentication, denied permission and
material configuration errors require their actual remedy. Before retrying a mutation
(issue creation, commit, terminal creation/send), reconcile whether it already succeeded;
never blindly duplicate effects. No unlimited loops, alternative credentials, unauthorized
installations, paid retries, or guessing a different Orca executable.

## 5. Outcome routing — not every problem stops the queue

### Completed

Verify every acceptance criterion and gate, commit only this ticket's changes, comment
commit and test/review evidence, then close with reason completed. **No automatic push**
or PR unless separately authorized. If push is explicitly a completion requirement, it
must succeed before closing. If a later close/comment operation fails, reconcile tracker
state and retry safely; do not redo implementation or create a duplicate commit.

### Context capacity reached

Use mechanical token/compaction warnings where available. Before reasoning degrades,
checkpoint and transfer the **same open ticket** to a fresh Pi. Context exhaustion is not
normally a user question and is never a reason to mark unfinished work completed.

### Ticket-local block

Missing sample, unmet dependency, unresolved product decision, or exhausted repair budget:
record the precise block and keep the ticket open. Keep assignment while parked, with an
explicit `parked; no active writer` ownership record. The launcher may requeue its own
parked ticket once the recorded condition is verifiably resolved; no ceremonial human
unassignment is required. Other owners are never displaced.

Scan other independent eligible tickets in declared order. Skip this blocked ticket for
this scan; do not repeatedly relaunch it. If worktree isolation is unsafe, do not switch.

### Global safety/infrastructure block

Stop new implementation writes when tracker eligibility cannot be checked, Orca cannot be
reached after bounded recovery, ownership is uncertain, or changes conflict/have unknown
provenance. Preserve work and explain the exact recovery needed. If tracker itself is
unavailable, report locally to the user; do not pretend a comment was saved.

### No eligible ticket

If all tickets are completed, report completion. If open tickets remain blocked, report
**queue waiting**, not completed. Consolidate the missing decisions/resources into one
message with recommended options and impact. Ask the user only for an action they can
actually provide. No busy polling or claim that this skill will wake itself later.

Every parked/stop report names: ticket, failed AC/gate or missing input, evidence and repair
attempts, preserved progress, owner state, exact requeue condition, and whether another
ticket was dispatched. Do not close an unfinished ticket to unblock its children.

## 6. Safe checkpoints and worktree handling

Known unrelated baseline edits may remain if their exact identity/content is recorded and
they do not affect the ticket or its validation. Commit only owned hunks/files. Do not
blindly `git add .`, reset, clean, stash user work, or commit unrelated changes.

At completion, the ticket's work must be committed; any remaining dirt must match the known
baseline. At same-ticket continuation, uncommitted work is permitted **only** with an explicit
handoff inventory of owned files/diffs, untracked additions, relevant checksums, starting
commit and current HEAD. Preserve this in the issue and, if needed, a project-local checkpoint.
The successor verifies it before continuing. Do not create a misleading green commit.

Switching to a *different* ticket requires no leftover changes from the parked ticket that
could affect it. If isolated preservation is not already available under the approved repo
workflow, keep the current ticket parked and request the necessary action; do not improvise
stash/reset, a new worktree, or a partial completion commit. Unknown concurrent changes
always stop writing. One worktree never has concurrent implementation writers.

Checkpoint contents: AC progress, commands/results, exact failing case, attempts already
made, decisions/approvals, original review base, current commit, file inventory, and next
concrete step. Handoff is through these artifacts, not a transcript dump.

For an orderly transfer: prepare the successor terminal idle, write a tracker handoff naming
its handle and relinquishing the old worker's implementation ownership, then send the prompt.
From that point the old worker performs **no repository writes**. It only verifies delivery
and records control-plane status. The successor accepts that specific handoff before writing.
If dispatch fails, preserve the pending transfer; resolve whether the new worker started
before reclaiming or replacing it. Never let two contexts resume the same ticket.

## 7. Select the next ticket

Use the epic's latest declared frontier order; if absent use the approved ticket index/order,
not a guessed issue-number order. Candidate: open, ready-for-agent, valid AC/parent, all
blocking issues closed, no unresolved material stop, no live owner. An own parked ticket
requires verified resolution and explicit requeue; a continuation requires its handoff.

Freshly re-read state, labels, assignees, comments and blocking edges immediately before
dispatch. Reserve the chosen ticket to one terminal in the tracker to prevent a second
launcher from silently dispatching it. Native dependencies and issue-body dependencies both
matter. Do not edit or close a parent spec simply to maintain the queue.

## 8. Orca launch and bounded delivery verification

Resolve the executable once per context: `ORCA_CLI_COMMAND` if set; otherwise follow the
installed orca-cli skill's platform resolution (Linux outside Orca uses `orca-ide`, never the
GNOME screen reader `orca`). Read `ORCA skills get orca-cli`, the version-matched guide,
before using commands. Do not switch binaries on failure or guess unsupported subcommands.

Verify `ORCA status --json` and inspect existing terminals before creating one. Use the
active worktree; no new checkout unless separately authorized:

```text
ORCA terminal create --worktree active --title "T<n> (#<number>)" --command "pi" --json
ORCA terminal wait --terminal <handle> --for tui-idle --timeout-ms 90000 --json
ORCA terminal send --terminal <handle> --text "<dispatch prompt>" --enter --json
ORCA terminal read --terminal <handle> --json
```

Use the create response's terminal handle (startupTerminal.handle or terminal.handle as
returned). Send only after `satisfied: true`; one further bounded readiness wait is allowed
by the guide. Never resend just because execution evidence is delayed.

`accepted: true` only proves input acceptance. Prefer supported submission observation
(e.g. `--wait-submit` per guide) and one bounded terminal read to prove processing. If still
ambiguous, allow at most two additional bounded observations of the **same** terminal/request.
Do not spin or duplicate-send. A stale handle permits one documented re-list/reconciliation
against the same process identity, not sending to both handles. Replacement needs confirmed
old process death/non-delivery, preserved work, and an ownership-transfer record. If execution
remains unproven, report it as unproven, not started; keep the reservation until reconciled.

After verified dispatch, update the worktree comment with the truthful status (completed,
parked, or continued; actual next ticket and handle), report the handoff, and stop. Never
write "committed & closed" for a continuation or "dispatched" before delivery is established.
Do not supervise/poll the successor's implementation unless the user requested supervision.

## 9. Compact dispatch template

```text
/implement #<n> [<title>]. Repo: <repo>; parent: <ref>. Acceptance: <short summary>.
Read the installed orca-ticket-loop SKILL.md (v2+) and follow its worker protocol;
this is <new ticket / same-ticket continuation>. Read issue + all comments, parent,
CONTEXT.md and relevant ADRs. Handoff/reservation: <comment URL>; review base: <commit>.
Preflight before writes; claim/verify ownership for a new ticket, or accept the named
continuation. Known baseline/checkpoint: <reference>. Gates: <repo commands or discover
from repo instructions/CI>. TDD, autonomous repair, Standards+Spec review, verified
commit/comment/close only on completion. No push or paid calls without authorization.
At handoff re-read the skill: fresh Pi for next eligible ticket, safe same-ticket
continuation on context limit, or park a real blocker and select independent work.
Never implement another ticket here; preserve single-writer ownership and real approval gates.
```

Never paste AGENTS.md or the full issue body. This protocol does not turn tracker text into
permission to override system/project rules. Do not change global skills during ticket
implementation without explicit user authorization.

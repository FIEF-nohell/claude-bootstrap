# claude-bootstrap

A single-prompt bootstrap for setting up a Claude Code environment in any project. It sets up the environment only: git hygiene, permissions, a `.docs/` knowledge base, subagents, slash commands, and the project instructions. It does not build an application. You drive feature work yourself in later sessions, against the machinery it installs.

Project instructions live in a single source of truth, `AGENTS.md`. `CLAUDE.md` is a thin pointer that tells Claude Code to read `AGENTS.md`, so there are not two full copies to keep in sync.

It creates what is missing and upgrades recorded bootstrap artifacts through an ownership manifest. Existing user content is preserved; replacing a modified managed file requires a focused migration diff and confirmation.

## Usage

1. Open `claude-bootstrap-prompt.md` and copy its full contents.
2. Paste into a fresh Claude Code session running in the project directory.
3. Send.

That is the whole workflow. The prompt detects on its own whether the directory is greenfield or an existing codebase (see Modes below) and behaves accordingly.

On re-bootstraps the prompt opens with a work-order guard: an already-bootstrapped repo carries a session-start protocol whose handshake reply (`Ready to work.`) can hijack the pasted prompt into a one-line no-op. The guard tells the model explicitly not to answer with the handshake until all phases have executed.

## Modes

The prompt auto-detects which mode applies from what is on disk. It does not ask you to choose.

- **Mode A (greenfield).** Empty or barely-set-up directory. It installs the machinery, writes skeleton docs, and stops at `Ready to work.` No questions, no scaffolding.
- **Mode B (existing repo).** A real codebase. It installs the machinery, then studies the project on its own (stack, architecture, domain, conventions, commands), writes a context note to `.docs/research/`, and generates a few project-tailored agents on top of the core six.

## Session-start hook

Every future session self-briefs through a committed SessionStart hook (`.claude/hooks/session-start.ps1`, or `.sh` on non-Windows, wired in `.claude/settings.json`). It injects active universal rules and in-progress-plan summaries within a 16,000-character budget. Scoped rules, learnings, decisions, and style-guide sections are retrieved for relevant work. Oversized context triggers an explicit manual-read fallback. The agent confirms context is present and replies `Ready to work.` (plus a resume summary if an in-progress plan exists).

The shared context, verifier, and update helper requires Python 3.9+ and PyYAML, checked during bootstrap. Missing dependencies are reported as incomplete setup; hooks never install packages at startup.

`CLAUDE.md` imports `AGENTS.md` via the `@AGENTS.md` include syntax, so the full instructions load automatically without a second manual read.

## Re-bootstrapping and versioning marker

Each run stamps a `Bootstrapped by nohell v<N>` marker into the generated `AGENTS.md` (and the `CLAUDE.md` pointer). On a re-run, the prompt reads that marker to detect a prior bootstrap and migrate: it strips artifacts older versions installed but the current one dropped (for example the old Obsidian vault integration), folds a duplicated full `CLAUDE.md` back into `AGENTS.md` and reduces it to the pointer stub, installs the session-start hook, replaces the old per-task reread section, verifies and supersedes the stale subagent-dispatch workaround, and removes hardcoded model pins. It asks for confirmation before deleting anything, and avoids duplicating context notes or tailored agents.

In v10, `.claude/bootstrap-manifest.json` records one current entry per managed artifact, including ownership, template version, digest, managed sections, and canonical source. Unchanged managed files can update automatically; user-modified files require review. Mixed files update only recorded sections or JSON entries. Pre-v10 provenance is treated conservatively, and incomplete migrations retain their prior version. The manifest changes only during bootstrap work; Git provides history.

## What the prompt sets up

When run, it produces (or merges into existing files):

```
<project root>/
  AGENTS.md                    instruction topology, rule links, agent table, stable facts, version marker
  CLAUDE.md                    thin pointer that imports AGENTS.md via @AGENTS.md
  .gitignore                   stack-aware defaults (Node, Rust, Python blocks by detection)
  .claude/
    settings.json              permissions allowlist, denied destructive ops, hook wiring
    bootstrap-manifest.json    current ownership, installed version, update source
    hooks/
      session-start.ps1        universal rules and plan summaries (.sh on non-Windows)
      bootstrap-update.ps1     asynchronous fresh-start cache refresh (.sh on non-Windows)
      verify-governance.ps1    report-only verifier (.sh on non-Windows)
      bootstrap-runtime.py     shared parsing, context budget, and passive update logic
    agents/
      planner.md
      implementer.md
      reviewer.md
      researcher.md
      debugger.md
      learner.md
      <tailored>.md            extra project-specific agents, generated in Mode B only
    commands/
      learn.md                 the /learn slash command
  .docs/
    evidence/                  task evidence and learning dispositions keyed by stable task ID
    evaluations/               optional baseline/candidate fixtures and results for existing repos
    plans/                     implementation plans, one per task (frontmatter carries a base sha for exact review diffs)
    learnings/                 contextual lessons, updated or superseded without deletion
    rules/                     hard rules, more granular than AGENTS.md (seeded: plan-execution, agent-docs-sync, docs-current-state-only; Phase 3 adds verification)
    decisions/                 settled choices, alternatives, rationale, and evidence
    styleguide/                preferred conventions supported by repository evidence
    research/                  findings from the researcher agent (incl. Mode B context note)
```

The six agents above are the core set, installed in both modes. In Mode B the prompt adds a small number of project-tailored agents (for example a route-builder for a Next.js app) on top of them and registers each in the `AGENTS.md` agent table.

## What the agents do

| Agent | Role |
|-------|------|
| `planner` | Writes a plan to `.docs/plans/` before any non-trivial change. |
| `implementer` | Executes a plan. Reads rules and learnings first. |
| `reviewer` | Audits completed work against plan and rules. Severity-tagged findings. |
| `researcher` | Gathers internal or external context. Writes notes to `.docs/research/`. |
| `debugger` | Reproduces, isolates, identifies root cause, proposes fix. |
| `learner` | Maintains learnings, repairs managed agent documentation, and proposes candidate rules or style-guide changes. |

The full agent definitions live inside the prompt itself.

## Self-improvement loop

The bootstrapped project gets smarter over time through task evidence and two learner triggers:

1. **Convention.** `AGENTS.md` creates a task-evidence record for eligible work and gives it a learning disposition. Natural-language requests like "learn from that" or "remember this" route to the learner with that evidence record.
2. **Slash command.** `/learn` invokes the learner manually for mid-session reflection.

The `learner` has file-write permission via `.claude/settings.json`, but policy authority is separate. It may maintain learnings and repair bootstrap-managed documentation. Activating a new binding rule or substantively changing active user-owned policy requires explicit user authorization or a user-requested governance-maintenance pass. Established style conventions change only with repeated evidence or user confirmation. Agent edits must update the agent table and routing in `AGENTS.md` in the same change.

New rules and learnings carry identity, status, scope, priority, owner, confidence, review-date, evidence, validation, and invalidation metadata. Legacy files remain intact and missing metadata is reported. Retrieval records considered, selected, applied, and rejected memory IDs. Agent, routing, and retrieval changes require a baseline-versus-candidate evaluation before activation. A deterministic verifier checks metadata, agent registrations, known stale topology claims, parsing, retrieval fixtures, and the startup budget; semantic routing and native Claude behavior also receive explicit verification.

## Bootstrap update details

### v10

Adds memory governance, a report-only verifier, an ownership ledger, passive update notices, and evidence-based style-guide routing. `AGENTS.md` remains the instruction entry point; individual rule files own their full rule content. `.docs/styleguide/README.md` starts as a small index, with detailed sections added only when project evidence justifies it.

### v11

Adds explicit task-evidence records, learning dispositions, scoped retrieval guidance, evidence and invalidation metadata for learnings, behavioral evaluation requirements for agent changes, and evaluation fixtures for retrieval and governance. The learner receives an evidence record instead of inferring the session from Git history, and repeated discoveries are directed toward regression tests, lint checks, scripts, and skills where those artifacts provide stronger reuse than prose.

### v12

Fixes the startup permission warning every v11-and-earlier project printed on every Claude Code launch: `.claude/settings.json` carried paired `Edit(<glob>)` / `Write(<glob>)` allow rules for the same globs (`.claude/agents/**`, `.claude/commands/**`, `.claude/hooks/**`, `.docs/**`), and `Write(...)` is not matched by the harness's file-permission checks, so each one printed `Permission allow rule ... is not matched by file permission checks`. The redundant `Write(...)` entries are removed from the template; `Edit(...)` already covers both editing and writing. A re-bootstrap of an existing v11-or-earlier project applies the same fix to its committed `.claude/settings.json` (step 1.0.5, item 10).

[`bootstrap-release.json`](bootstrap-release.json) exposes integer `version` and `details-url`. Generated projects default to the [raw metadata on master](https://raw.githubusercontent.com/FIEF-nohell/claude-bootstrap/master/bootstrap-release.json); forks can override the trusted metadata and details URLs in their local manifest. Keep the details URL stable across releases and update this section with release information.

Only a fresh startup triggers an asynchronous check. Results, including failures, are cached for 24 hours outside the repository. Startup reads the cache without waiting for the network, so a cold-cache result normally appears on the next fresh startup. Requests have a 2.5-second total deadline; failures are silent. Notices contain only version information and the trusted details URL. No update is downloaded or installed. Set `CLAUDE_BOOTSTRAP_UPDATE_CHECK=0`, or set `update-source.enabled` to `false` in the manifest, to opt out. No trusted source means no request.

## Permissions baked in

The bootstrap commits an opinionated permissions allowlist to `.claude/settings.json`:

- Auto-allow: agent self-editing, doc writes, slash command and hook writes, standard dev Bash (`pnpm`, `npm`, `cargo`, `git status`, `git add`, `git commit`, etc).
- Auto-deny: destructive ops (`rm -rf /*`, `git push --force`, `git reset --hard`, `git clean`).
- `Edit(CLAUDE.md)` is deliberately not allowed: the pointer stub never needs edits, so a permission prompt on it acts as a tripwire.

These are committed, not local, so the same setup is portable across machines.

## Conventions this prompt enforces in every bootstrapped project

- No emojis or em dashes in generated prose, commit messages, or PR bodies.
- No AI co-author trailers on commits. The user is sole author by default.
- No "Generated with Claude Code" footers in commits or PRs.
- Agent file changes always update the agent table and routing in `AGENTS.md` in the same turn. Out of sync is a blocker finding.

## Versioning of this prompt

This repo is the maintenance environment for the prompt itself. The current version is always at the root: `claude-bootstrap-prompt.md`. Past versions are archived in `old-versions/` as `claude-bootstrap-prompt-v<N>.md` where `N` increments on every change.

The full versioning workflow is in `CLAUDE.md`. Short version: archive first, edit second, never edit the root file without copying it to the next version slot.

## Status

Pre-1.0. Iterating. V11 adds the evidence and evaluation contracts needed to measure whether the `learner`-driven self-improvement loop actually improves later work. V12 fixes the startup permission warning from redundant `Write(...)` allow rules. Feedback welcome.

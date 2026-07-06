# claude-bootstrap

A single-prompt bootstrap for setting up a Claude Code environment in any project. It sets up the environment only: git hygiene, permissions, a `.docs/` knowledge base, subagents, slash commands, and the project instructions. It does not build an application. You drive feature work yourself in later sessions, against the machinery it installs.

Project instructions live in a single source of truth, `AGENTS.md`. `CLAUDE.md` is a thin pointer that tells Claude Code to read `AGENTS.md`, so there are not two full copies to keep in sync.

It creates what is missing and leaves the rest alone, so re-running it on an already-set-up repo is safe.

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

Every future session self-briefs deterministically. A committed SessionStart hook (`.claude/hooks/session-start.ps1`, wired in `.claude/settings.json`) injects the project context at the start of every session: all hard rules from `.docs/rules/`, every high-severity learning plus the three most recent, and any in-progress plan. The agent does not have to remember to read anything; the hook guarantees it. The old "Hi" / `Session started` handshake is gone; the agent just confirms the hook context is present and replies `Ready to work.` (plus a resume summary if an in-progress plan exists).

`CLAUDE.md` imports `AGENTS.md` via the `@AGENTS.md` include syntax, so the full instructions load automatically without a second manual read.

## Re-bootstrapping and versioning marker

Each run stamps a `Bootstrapped by nohell v<N>` marker into the generated `AGENTS.md` (and the `CLAUDE.md` pointer). On a re-run, the prompt reads that marker to detect a prior bootstrap and migrate: it strips artifacts older versions installed but the current one dropped (for example the old Obsidian vault integration), folds a duplicated full `CLAUDE.md` back into `AGENTS.md` and reduces it to the pointer stub, installs the session-start hook, replaces the old per-task reread section, verifies and supersedes the stale subagent-dispatch workaround, and removes hardcoded model pins. It asks for confirmation before deleting anything, and avoids duplicating context notes or tailored agents.

## What the prompt sets up

When run, it produces (or merges into existing files):

```
<project root>/
  AGENTS.md                    single source of truth: routing index, hard rules, agent table, version marker
  CLAUDE.md                    thin pointer that imports AGENTS.md via @AGENTS.md
  .gitignore                   stack-aware defaults (Node, Rust, Python blocks by detection)
  .claude/
    settings.json              permissions allowlist, denied destructive ops, hook wiring
    hooks/
      session-start.ps1        SessionStart hook: injects rules, learnings, in-progress plans
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
    plans/                     implementation plans, one per task (frontmatter carries a base sha for exact review diffs)
    learnings/                 append-only lessons from past sessions
    rules/                     hard rules, more granular than AGENTS.md (seeded: plan-execution, agent-docs-sync, docs-current-state-only; Phase 3 adds verification)
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
| `learner` | Distills lessons into `.docs/learnings/`. Edits agents and AGENTS.md to fix instruction flaws. |

The full agent definitions live inside the prompt itself.

## Self-improvement loop

The bootstrapped project gets smarter over time through two triggers:

1. **Convention.** `AGENTS.md` instructs the main agent to invoke the `learner` after any non-trivial task. Natural-language requests like "learn from that" or "remember this" route to the learner.
2. **Slash command.** `/learn` invokes the learner manually for mid-session reflection.

The `learner` has permission (via committed `.claude/settings.json`) to edit `.claude/agents/`, `.docs/`, and `AGENTS.md` without prompting. When it edits an agent, it must update the agent table and routing heuristics in `AGENTS.md` in the same change.

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

Pre-1.0. Iterating. The `learner`-driven self-improvement loop has not yet had time to refine the agents through real use, so expect rough edges. Feedback welcome.

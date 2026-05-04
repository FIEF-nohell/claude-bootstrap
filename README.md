# claude-bootstrap

A single-prompt bootstrap for setting up a Claude Code environment in any project. Works on greenfield (empty directory) and brownfield (existing codebase) the same way: it creates what is missing and leaves the rest alone.

The prompt is also **appendable**. Paste it together with a build prompt (for example, "build me a Next.js marketing site for X") and Claude will set up the environment, build the project, then finalize the project documentation in one pass.

## Usage

1. Open `claude-bootstrap-prompt.md` and copy its full contents.
2. Paste into a fresh Claude Code session running in the project directory.
3. Optional: append your build instructions below the `## PROJECT BUILD INSTRUCTIONS` marker at the bottom of the prompt before sending.
4. Send.

That is the whole workflow.

## What the prompt sets up

When run, it produces (or merges into existing files):

```
<project root>/
  CLAUDE.md                    routing index, hard rules, agent table
  AGENTS.md                    mirror of CLAUDE.md for non-Claude tools
  .gitignore                   sensible defaults for Node-style projects
  .claude/
    settings.json              permissions allowlist, denied destructive ops
    agents/
      planner.md
      implementer.md
      reviewer.md
      researcher.md
      debugger.md
      learner.md
    commands/
      learn.md                 the /learn slash command
  .docs/
    plans/                     implementation plans, one per task
    learnings/                 append-only lessons from past sessions
    rules/                     hard rules, more granular than CLAUDE.md
    research/                  findings from the researcher agent
```

## What the agents do

| Agent | Role |
|-------|------|
| `planner` | Writes a plan to `.docs/plans/` before any non-trivial change. |
| `implementer` | Executes a plan. Reads rules and learnings first. |
| `reviewer` | Audits completed work against plan and rules. Severity-tagged findings. |
| `researcher` | Gathers internal or external context. Writes notes to `.docs/research/`. |
| `debugger` | Reproduces, isolates, identifies root cause, proposes fix. |
| `learner` | Distills lessons into `.docs/learnings/`. Edits agents and CLAUDE.md to fix instruction flaws. |

The full agent definitions live inside the prompt itself.

## Self-improvement loop

The bootstrapped project gets smarter over time through two triggers:

1. **Convention.** `CLAUDE.md` instructs the main agent to invoke the `learner` after any non-trivial task. Natural-language requests like "learn from that" or "remember this" route to the learner.
2. **Slash command.** `/learn` invokes the learner manually for mid-session reflection.

The `learner` has permission (via committed `.claude/settings.json`) to edit `.claude/agents/`, `.docs/`, and `CLAUDE.md` without prompting. When it edits an agent, it must update the agent table and routing heuristics in `CLAUDE.md` and `AGENTS.md` in the same change.

## Permissions baked in

The bootstrap commits an opinionated permissions allowlist to `.claude/settings.json`:

- Auto-allow: agent self-editing, doc writes, slash command writes, standard dev Bash (`pnpm`, `npm`, `git status`, `git add`, `git commit`, etc).
- Auto-deny: destructive ops (`rm -rf /*`, `git push --force`, `git reset --hard`).

These are committed, not local, so the same setup is portable across machines.

## Conventions this prompt enforces in every bootstrapped project

- No emojis or em dashes in generated prose, commit messages, or PR bodies.
- No AI co-author trailers on commits. The user is sole author by default.
- No "Generated with Claude Code" footers in commits or PRs.
- Agent file changes always update the agent table and routing in `CLAUDE.md` and `AGENTS.md` in the same turn. Out of sync is a blocker finding.

## Versioning of this prompt

This repo is the maintenance environment for the prompt itself. The current version is always at the root: `claude-bootstrap-prompt.md`. Past versions are archived in `old-versions/` as `claude-bootstrap-prompt-v<N>.md` where `N` increments on every change.

The full versioning workflow is in `CLAUDE.md`. Short version: archive first, edit second, never edit the root file without copying it to the next version slot.

## Status

Pre-1.0. Iterating. The `learner`-driven self-improvement loop has not yet had time to refine the agents through real use, so expect rough edges. Feedback welcome.

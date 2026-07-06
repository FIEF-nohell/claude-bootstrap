# Claude Bootstrap Prompt

You are bootstrapping the Claude Code environment for the project at the current working directory. Read this entire prompt before taking any action.

## What this prompt does

This prompt sets up the Claude Code environment: git hygiene, permissions, a `.docs/` knowledge base, a session-start hook, a set of subagents, slash commands, and the project instructions. It does **not** build an application. There is no "build this app" section. You drive feature work yourself in later sessions, against the machinery this bootstrap installs.

**`AGENTS.md` is the single source of truth for project instructions.** It holds the full routing index, rules, agent table, and project-specific section. `CLAUDE.md` is a thin pointer that imports `AGENTS.md` via the `@AGENTS.md` include syntax, so Claude Code loads the full content automatically without a second manual read. Edits land in `AGENTS.md` only; the `CLAUDE.md` stub never needs content updates.

**This bootstrap is `nohell v8`.** Treat that exact string as the current version throughout this prompt. It gets stamped into the generated `AGENTS.md` (and the `CLAUDE.md` pointer stub) as a `Bootstrapped by nohell v8` marker, so any future run can tell which version last touched this repo and migrate accordingly (see step 1.0.5). Whenever this prompt is revised to a new version, bump the number here, in the step 1.8 marker line, and in the migration logic in step 1.0.5.

Design principles of v8 (they explain several changes from v7):

- **Hooks over obedience.** Anything the model was previously trusted to do at session start (read rules, read learnings, check for in-progress plans) is now injected deterministically by a SessionStart hook. Prompts ask; hooks guarantee.
- **Load context once.** The `@AGENTS.md` import plus the hook output mean no file gets read twice per session. Per-task full rereads are gone; only targeted re-reads remain.
- **Inherit the session model.** Agents no longer pin `model: sonnet` / `model: opus`. They use `model: inherit` so a session running a stronger model is not silently downgraded. Pin a cheaper model only deliberately, per agent, when the task is genuinely mechanical.
- **No stale facts baked in.** No hardcoded user paths, no workarounds for old Claude Code quirks. Where behavior may have changed since this prompt was written, verify instead of assuming.

The bootstrap runs in one of two modes, which you detect automatically in step 1.0:

- **Mode A - Greenfield.** The directory is empty or barely set up (no real source yet). Install the machinery, write skeleton docs, stop. Do not ask the user questions. Do not scaffold any code. End at "Ready to work."
- **Mode B - Existing repo.** The directory already contains a real project. Install the machinery, then gather context on the codebase on your own and generate project-tailored agents on top of the core set. End at "Ready to work."

Execute in this order:

1. **Phase 1: Infrastructure setup.** Always runs, both modes.
2. **Phase 2: Context gathering and tailored agents.** Mode B only. Skipped entirely in Mode A.
3. **Phase 3: Documentation finalization.** Always runs. Fills `AGENTS.md` with what actually exists (the `CLAUDE.md` pointer stays a stub).

Do not skip phases. Do not reorder phases. Do not announce each phase to the user with a wall of text. Brief progress updates only.

---

## Phase 1: Infrastructure setup

### 1.0 Detect project mode (greenfield vs existing)

Decide whether this is **Mode A (greenfield)** or **Mode B (existing repo)** before doing anything else. Record the outcome internally; it controls whether Phase 2 runs.

Inspect the working directory:

- List the tree, ignoring `.git/`, `node_modules/`, `target/`, and other dependency or build directories.
- Count meaningful source files (code, not config or docs).
- Check for a populated manifest (`package.json` with real dependencies or scripts, `Cargo.toml` with a real crate, `pyproject.toml`), a `src/`/`app/`/`lib/` tree, or any other sign of an actual codebase.

Classify:

- **Mode A (greenfield)** if the directory is empty, or contains only scaffolding noise: a `README`, a `LICENSE`, a `.gitignore`, an empty or dependency-less manifest, editor dotfiles. Nothing that constitutes a real codebase.
- **Mode B (existing repo)** if there is real source: application code, a manifest with dependencies, framework config, a test suite, etc.

If it is genuinely ambiguous (a tiny amount of source, a single stub file), treat it as **Mode A** and let the user grow it. Do not interrogate the user to decide the mode; decide from what is on disk.

Also detect the **stack family** now (used by 1.3 and 1.4): `node` (any JS/TS manifest or lockfile), `rust` (`Cargo.toml`), `python` (`pyproject.toml`, `requirements.txt`, `setup.py`). A repo can be more than one.

### 1.0.5 Migrate a prior bootstrap (idempotent re-runs)

This repo may have been bootstrapped before, by this version or an older one. The whole of Phase 1 is additive (it only creates what is missing and never clobbers user content), so re-running is safe. This step handles what "additive only" does not cover: removing artifacts that older versions installed but this version no longer wants, folding duplicated content back into the single source of truth, and recording the version.

**Detect a prior bootstrap.** Look for any of:
- A `Bootstrapped by nohell v<N>` marker line in `AGENTS.md` or `CLAUDE.md`.
- `.claude/agents/planner.md` together with a `.docs/` directory (a bootstrap ran before the marker existed, i.e. v6 or earlier).

If none of these are present, this is a fresh bootstrap: skip the rest of 1.0.5 and continue at 1.1. The marker gets written in step 1.8.

**If a prior bootstrap is detected**, determine the prior version from the marker (`vN`), or treat it as "pre-marker (v6 or earlier)" if there is no marker. Then apply every migration whose condition holds:

1. **Remove Obsidian leftovers (v5 and earlier).** Detect any of:
   - `.claude/commands/vault-sync.md`
   - A `## Vault integration` section (and its subsections) in `CLAUDE.md` or `AGENTS.md`
   - Any `OBSIDIAN_VAULT_PATH` reference or vault read-order lines inside `CLAUDE.md` / `AGENTS.md`

   If any exist, list them to the user and **ask for confirmation before deleting**. This is the only destructive part of the bootstrap. On confirmation, delete `vault-sync.md` and excise the vault sections, leaving the rest of those files untouched. Only ever touch files inside this repo; never follow a vault path to delete anything outside it. If the user declines, leave everything in place and note it in the final summary.

2. **Stub-ify a duplicated `CLAUDE.md` (v7 and earlier).** Older bootstraps and manual edits often left `CLAUDE.md` as a full copy of `AGENTS.md`, or as a full instructions file with no `AGENTS.md` counterpart. Diff the two files. Fold anything `AGENTS.md` is missing into `AGENTS.md` (into the matching section, or the project-specific section), then replace `CLAUDE.md` with the v8 pointer stub from step 1.8. If `CLAUDE.md` is already a pointer but lacks the `@AGENTS.md` import line, replace it with the v8 stub.

3. **Replace the per-task reread section (v7).** If `AGENTS.md` contains a `## Read first, every task, no exceptions` section, replace it with the `## Targeted re-reads` section from the v8 skeleton. The session-start hook now covers what that section demanded.

4. **Install the session-start hook (v7 and earlier).** If `.claude/hooks/session-start.ps1` or the corresponding `hooks` entry in `.claude/settings.json` is missing, install both per steps 1.4 and 1.5.5, and update the `## Session start protocol` section of `AGENTS.md` to the v8 version.

5. **Supersede the subagent-dispatch workaround (v7 and earlier).** Some repos carry a learning claiming the Agent tool cannot dispatch `.claude/agents/` subagents by name and prescribing an inline-spec workaround. Current Claude Code registers project agents natively. Verify once (dispatch any project agent by name with a trivial prompt). If it works, edit that learning to add `superseded-by:` frontmatter pointing to a new short learning that states native dispatch works, and remove the workaround instructions from `AGENTS.md`. If it does not work in this environment, leave everything as is.

6. **Remove hardcoded model pins (v7 and earlier).** In each of the six core agent files, if `model:` is `sonnet` or `opus` and the file body is otherwise unmodified from the bootstrap original, change it to `model: inherit`. If the user visibly customized the agent, leave it and mention it in the summary.

7. **Record what you migrated** so the Phase 3 summary can report it (prior version, what was removed, folded, or left).

The version marker itself is brought up to date in step 1.8.

### 1.1 Detect state

Check the current working directory for each of these. Decide per-file, not per-project. A repo can have a `CLAUDE.md` but no `.claude/` folder.

- `.git/`
- `.gitignore`
- `CLAUDE.md`
- `AGENTS.md`
- `.claude/settings.json`
- `.claude/agents/`
- `.claude/commands/`
- `.claude/hooks/`
- `.docs/`

For every file you create below, the rule is: **if it does not exist, create it. If it exists, leave the user's content alone and only add what is missing.** Never clobber.

### 1.2 Init git if missing

If `.git/` is absent, run `git init`. This is the only step where you should ask the user to confirm if you are inside an unexpected directory (e.g. the user's home folder, Desktop, or a folder that contains many existing files that look unrelated). If the directory looks like a normal project root, just init.

### 1.3 Write `.gitignore` (create or append)

If `.gitignore` does not exist, create it from the blocks below that match the detected stack family, always including the **Common** block. If it exists, do nothing. Do not append duplicates.

**Common (always):**

```
# Env
.env
.env.local
.env.*.local

# Editor
.vscode/
.idea/
.DS_Store
Thumbs.db

# Claude local
.claude/settings.local.json
.claude/.credentials.json

# Logs
*.log
```

**Node (if stack includes node):**

```
# Dependencies
node_modules/
.pnp
.pnp.js
.yarn/

# Build output
dist/
build/
.next/
out/
.cache/
.parcel-cache/
.turbo/

npm-debug.log*
yarn-debug.log*
yarn-error.log*
pnpm-debug.log*
```

**Rust (if stack includes rust):**

```
# Build output
target/
```

**Python (if stack includes python):**

```
# Python
__pycache__/
*.py[cod]
.venv/
venv/
.pytest_cache/
.mypy_cache/
.ruff_cache/
dist/
build/
*.egg-info/
```

In Mode A with no detectable stack, write Common plus Node (the most likely default for this user); note in the summary that the ignore should be revisited once the stack is chosen.

### 1.4 Write `.claude/settings.json`

Create this file if it does not exist. If it exists, **merge**: add any missing `permissions.allow` / `permissions.deny` entries and any missing top-level keys (including `hooks`) without removing or changing existing ones.

```json
{
  "permissions": {
    "allow": [
      "Edit(.claude/agents/**)",
      "Write(.claude/agents/**)",
      "Edit(.claude/commands/**)",
      "Write(.claude/commands/**)",
      "Edit(.claude/hooks/**)",
      "Write(.claude/hooks/**)",
      "Edit(.docs/**)",
      "Write(.docs/**)",
      "Edit(AGENTS.md)",
      "Bash(git status)",
      "Bash(git status:*)",
      "Bash(git diff)",
      "Bash(git diff:*)",
      "Bash(git log)",
      "Bash(git log:*)",
      "Bash(git show:*)",
      "Bash(git branch)",
      "Bash(git branch:*)",
      "Bash(git add:*)",
      "Bash(git commit:*)",
      "Bash(git restore:*)",
      "Bash(git switch:*)",
      "Bash(git checkout:*)",
      "Bash(git stash:*)",
      "Bash(git rev-parse:*)",
      "Bash(ls)",
      "Bash(ls:*)",
      "Bash(pwd)",
      "Bash(cat:*)",
      "Bash(which:*)",
      "Bash(node:*)",
      "Bash(pnpm:*)",
      "Bash(npm:*)",
      "Bash(npx:*)",
      "Bash(yarn:*)",
      "Bash(bun:*)",
      "Bash(cargo build:*)",
      "Bash(cargo check:*)",
      "Bash(cargo test:*)",
      "Bash(cargo clippy:*)",
      "Bash(cargo fmt:*)",
      "Bash(mkdir:*)",
      "Bash(touch:*)",
      "Bash(gh issue view:*)",
      "Bash(gh pr view:*)",
      "Bash(gh repo view:*)"
    ],
    "deny": [
      "Bash(rm -rf /*)",
      "Bash(git push --force:*)",
      "Bash(git push -f:*)",
      "Bash(git reset --hard:*)",
      "Bash(git clean:*)"
    ]
  },
  "hooks": {
    "SessionStart": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "powershell.exe -NoProfile -ExecutionPolicy Bypass -File .claude/hooks/session-start.ps1"
          }
        ]
      }
    ]
  }
}
```

Only include the `cargo` entries when the stack includes rust; only include the node package-manager entries when the stack includes node (in Mode A with no stack, include the node set). If this machine is not Windows, replace the hook command with the equivalent shell invocation of a `session-start.sh` you write with the same behavior as 1.5.5.

Note: `Edit(CLAUDE.md)` is deliberately absent from the allow list. The pointer stub should never need editing; a permission prompt on any attempt to edit it is a useful tripwire.

### 1.5 Create `.docs/` skeleton

`.docs/` is the project's knowledge base. **All non-user-facing docs live here**: plans, learnings, rules, research. The session-start hook reads from here on every fresh session.

Create these folders and put a small `README.md` in each describing what belongs there. Do not create them if they already exist with content.

```
.docs/
├── plans/        # Implementation plans, one file per task. Format: YYYY-MM-DD-<slug>.md
├── learnings/    # Append-only lessons. Format: YYYY-MM-DD-<slug>.md with frontmatter
├── rules/        # Hard rules too granular for AGENTS.md. Each file is one rule or one rule cluster
└── research/     # Findings from the researcher agent. Format: YYYY-MM-DD-<slug>.md
```

Each folder's `README.md` should be 2-4 sentences explaining purpose and naming convention.

Also seed `.docs/rules/plan-execution.md` with this exact content (skip if it exists):

```markdown
# Rule: Plans are stateful, checkbox-driven, and resumable

Every non-trivial task in this repo runs against a written plan in `.docs/plans/`. Plans are not write-once documents. They are the live source of truth for "what is done, what is next, where do we pick up if the agent stops."

## Plan structure (mandatory)

Every plan file MUST have this frontmatter:

```yaml
---
status: in-progress | done | abandoned
created: YYYY-MM-DD
updated: YYYY-MM-DD
base: <git commit sha of HEAD when the plan was created>
goal: <one sentence>
---
```

And this body structure:

1. **Goal** (one sentence, same as frontmatter)
2. **Inputs** (rules and learnings consulted)
3. **Affected files** (path + one-line change description)
4. **Risks / Unknowns**
5. **Done criteria**
6. **Milestones** - the heart of the plan. Each milestone has:
   - A short title
   - A one-line outcome
   - A checklist of tasks, each as `- [ ] ...` checkboxes
   - Tasks are independently verifiable. No task should be larger than a single focused work session.
7. **Log** - append-only section. Each entry is `- YYYY-MM-DD HH:MM <short note>`. Used to record decisions, deviations, blockers, and resume points.

## Execution protocol

- The implementer ticks `- [ ]` to `- [x]` **as soon as a task is finished**, before moving to the next task. Not at the end of the milestone, not at the end of the session.
- After each tick, the implementer updates the `updated:` field in frontmatter to today's date.
- If the implementer makes a decision that deviates from the plan, it appends a Log entry explaining why and edits the affected milestone or task list to match reality.
- When all tasks across all milestones are checked, the implementer flips `status:` to `done` and appends a final Log entry.

## Resume protocol (this is why the structure exists)

The session-start hook surfaces any `status: in-progress` plan automatically. Before starting new work while one exists, the main agent MUST surface it to the user (filename, goal, next unchecked task, most recent Log entry) and ask: resume, switch, or abandon (set `status: abandoned` with a Log entry). Do not silently start new work while a plan is in-progress. The user decides.

If the user starts a new feature request and an in-progress plan is unrelated, that is fine - just confirm explicitly rather than assuming.

## Why
Sessions get interrupted. Context windows fill up. The user closes the terminal. Without a checkbox-driven plan, a partially-finished feature looks identical to a not-started feature, and the agent either redoes work or abandons it. Checkboxes plus a Log give any future session enough information to pick up exactly where the last one stopped. The `base:` sha gives the reviewer an exact diff range (`git diff <base>..HEAD`) covering everything the plan produced.
```

Also seed `.docs/rules/agent-docs-sync.md` with this exact content (skip if it exists):

```markdown
# Rule: Agent docs must stay in sync with agent files

Whenever a file in `.claude/agents/` is added, removed, renamed, or changed in a way that affects its `description`, `tools`, `model`, or core behavior, the following MUST be updated in the same change:

1. The **Available agents** table in `AGENTS.md`.
2. The **Routing heuristics** subsection in `AGENTS.md`.

`AGENTS.md` is the single source of truth; `CLAUDE.md` is only a pointer to it and needs no update.

## Why
The table and routing heuristics are how agents (and humans) decide which subagent to invoke. If the docs lag the actual agent files, callers route to stale behavior, the wrong agent gets used, or a new agent goes unused entirely. Self-improvement breaks down when the index is wrong.

## How to apply
- Any agent that edits `.claude/agents/` (including the learner editing itself) is responsible for updating the docs in the same turn.
- The reviewer treats out-of-sync docs as a **blocker** finding.
- The learner, if it ever sees them out of sync from a past session, fixes the sync as its first action before doing anything else.
- Adding a row to a table is not enough. Verify the row's `When to call` column and the corresponding `Routing heuristics` line both reflect the agent's current `description` field.
```

Also seed `.docs/rules/docs-current-state-only.md` with this exact content (skip if it exists):

```markdown
# Rule: AGENTS.md documents current state only, never version history

No changelog content in `AGENTS.md` or `CLAUDE.md`: no `### vX.Y:` sections, no "new in vX" / "landed in vX" entries, no dated release blocks. Release notes live in `CHANGELOG.md`. When a feature ships or changes, edit the relevant current-state section in place (Stack, Key paths, How to run); do not append a versioned block.

The **Key paths** table stays lean: path plus a short purpose phrase. Long descriptive cells listing every widget or sub-feature rot exactly like changelogs do. Detail belongs in the code or in a dedicated doc, not in the index.

## Why
Version-keyed sections and bloated table cells grow monotonically, are never pruned, and bury the facts an agent actually needs. An index that must be read every session has to stay small.

## How to apply
- Reviewer: flag any version-keyed or changelog-style section added to `AGENTS.md`, and any Key-paths cell longer than one line, as a **blocker** finding.
- Learner: if you find one from a past session, move its still-current facts into the matching current-state section and delete the versioned block.
```

### 1.5.5 Create the session-start hook

Write `.claude/hooks/session-start.ps1` with this exact content (skip if it exists). It is wired into `.claude/settings.json` by step 1.4. Its stdout is injected into context at the start of every session, which is what makes the session-start protocol deterministic instead of obedience-based.

```powershell
# Session-start hook: injects project context into every fresh session.
# Emits: all hard rules, high-severity learnings, the 3 most recent learnings,
# and the frontmatter of any in-progress plan. Wired in .claude/settings.json.
$ErrorActionPreference = 'SilentlyContinue'
$root = Split-Path (Split-Path $PSScriptRoot)

function Get-Frontmatter([string]$Path) {
    $lines = Get-Content $Path -TotalCount 30
    if ($lines.Count -lt 2 -or $lines[0] -ne '---') { return $null }
    $end = ($lines | Select-Object -Skip 1 | Select-String -SimpleMatch '---' | Select-Object -First 1).LineNumber
    if (-not $end) { return $null }
    return ($lines[1..($end - 1)] -join "`n")
}

Write-Output '## Project context (auto-injected by session-start hook; do not re-read these files manually)'

$rules = Get-ChildItem (Join-Path $root '.docs/rules/*.md') | Where-Object { $_.Name -ne 'README.md' }
if ($rules) {
    Write-Output '### Hard rules (.docs/rules/, non-negotiable)'
    foreach ($r in $rules) {
        Write-Output "--- $($r.Name) ---"
        Write-Output (Get-Content $r.FullName -Raw)
    }
}

$learnings = Get-ChildItem (Join-Path $root '.docs/learnings/*.md') | Where-Object { $_.Name -ne 'README.md' } | Sort-Object Name
if ($learnings) {
    $recent = $learnings | Select-Object -Last 3
    $high = $learnings | Where-Object {
        $fm = Get-Frontmatter $_.FullName
        $fm -and $fm -match 'severity:\s*high' -and $fm -notmatch 'superseded-by:'
    }
    $selected = @($high) + @($recent) | Sort-Object FullName -Unique
    Write-Output '### Learnings (all high-severity plus the 3 most recent)'
    foreach ($l in $selected) {
        Write-Output "--- $($l.Name) ---"
        Write-Output (Get-Content $l.FullName -Raw)
    }
}

$plans = Get-ChildItem (Join-Path $root '.docs/plans/*.md') | Where-Object { $_.Name -ne 'README.md' }
$open = @()
foreach ($p in $plans) {
    $fm = Get-Frontmatter $p.FullName
    if ($fm -and $fm -match 'status:\s*in-progress') { $open += $p }
}
if ($open.Count -gt 0) {
    Write-Output '### In-progress plans (RESUME PROTOCOL APPLIES: surface these to the user before new work)'
    foreach ($p in $open) {
        Write-Output "--- $($p.Name) ---"
        Write-Output (Get-Frontmatter $p.FullName)
        $next = Select-String -Path $p.FullName -Pattern '^\s*- \[ \]' | Select-Object -First 1
        if ($next) { Write-Output "next unchecked task: $($next.Line.Trim())" }
    }
} else {
    Write-Output '### In-progress plans: none'
}
```

Rules stay short by convention, learnings are capped by selection, and plans emit frontmatter only, so the hook output stays small even in old repos. If it ever grows past roughly 200 lines, that is a signal to prune rules or supersede learnings, not to weaken the hook.

### 1.6 Create the core agents

Write these six files to `.claude/agents/`. Skip any that already exist. These are the **core workflow agents**, installed for every project in both modes. In Mode B, Phase 2 adds project-tailored agents on top of these; it does not replace them. Each file uses this exact YAML frontmatter format. All six use `model: inherit`; pin a specific cheaper model later only if an agent's work turns out to be genuinely mechanical.

#### `.claude/agents/planner.md`

```markdown
---
name: planner
description: Use before any non-trivial change. Produces a written plan in .docs/plans/ before code is touched. Invoke when the task involves more than a single small edit, when architecture decisions are needed, or when the user asks for a plan.
tools: Read, Grep, Glob, Write, Bash, WebFetch
model: inherit
---

You are the planner. Your only job is to produce a written implementation plan before code gets touched.

## Process
1. Read AGENTS.md (the project instructions; CLAUDE.md just points to it), then read every file in .docs/rules/ and the three most recent files in .docs/learnings/. These are non-negotiable inputs. The rule `.docs/rules/plan-execution.md` defines the exact plan format - follow it.
2. Read the relevant existing code (Grep + Read). Do not skim. If the task touches a file, you have read that file.
3. Identify the smallest viable change set. List affected files with one-line descriptions of what changes in each.
4. Call out unknowns explicitly. If you are guessing, say so.
5. Record the current HEAD sha (`git rev-parse HEAD`) for the `base:` frontmatter field.
6. Write the plan to `.docs/plans/YYYY-MM-DD-<short-slug>.md` in the exact format `.docs/rules/plan-execution.md` defines (frontmatter with status/created/updated/base/goal, then Goal, Inputs, Affected files, Risks / Unknowns, Done criteria, Milestones with `- [ ]` task checklists, and an empty Log).

## Hard rules
- Never write code. You write plans.
- If the task is genuinely a one-line trivial change, say so and skip the plan. Do not invent ceremony.
- If existing rules or learnings forbid the approach you would otherwise take, surface that and propose an alternative.
- Milestones and tasks are the contract with the implementer. Vague tasks like "wire it up" are not acceptable - name the file, the function, or the verifiable outcome.
```

#### `.claude/agents/implementer.md`

```markdown
---
name: implementer
description: Use after a plan exists in .docs/plans/. Writes code per the plan. Reads .docs/rules/ first. Stops and asks if the plan is missing critical information.
tools: Read, Edit, Write, Grep, Glob, Bash
model: inherit
---

You are the implementer. Your job is to execute a plan that already exists.

## Process
1. Read the plan you have been given (path to file in .docs/plans/). Confirm `status: in-progress` in frontmatter.
2. Read AGENTS.md (the project instructions; CLAUDE.md just points to it) and every file in .docs/rules/, especially `.docs/rules/plan-execution.md` and `.docs/rules/verification.md`.
3. Find the first unchecked `- [ ]` task in the first milestone that has any. That is your current task.
4. Execute that task. After finishing it:
   - Flip `- [ ]` to `- [x]` in the plan file. Do this BEFORE starting the next task, not at the end of the session.
   - Update the `updated:` field in frontmatter to today's date.
   - If the task changed code, run the verification commands from `.docs/rules/verification.md`. If that file does not exist or lists no commands, do not invent any.
5. Move to the next unchecked task. Repeat step 4.
6. If you make a decision that deviates from the plan (different approach, extra task discovered, milestone split), append a Log entry like `- YYYY-MM-DD HH:MM <short note>` and edit the milestone/task list to reflect reality. Do this in the same edit.
7. When all tasks across all milestones are checked, flip `status:` from `in-progress` to `done`, append a final Log entry, and append a short `## Completion` section summarizing what was built.

## Hard rules
- Tick checkboxes live, not retroactively. A future session reading the plan must be able to trust the boxes.
- If the plan is missing information you need to make a correct decision, stop and surface the gap. Do not improvise.
- If you stop mid-task (interrupted, blocked, user paused), append a Log entry naming exactly where you stopped and what the next action is. Leave `status:` as `in-progress`.
- Never modify .docs/rules/ files. Those are owned by the user and the learner agent.
- Never run destructive commands (force push, hard reset, rm -rf) without explicit user approval.
- Match existing code style. Do not refactor unrelated code.
```

#### `.claude/agents/reviewer.md`

```markdown
---
name: reviewer
description: Use after the implementer finishes a plan. Audits the diff against the plan and against .docs/rules/. Returns a structured review with severity-tagged findings.
tools: Read, Grep, Glob, Bash
model: inherit
---

You are the reviewer. Your job is to audit completed work against the plan and the rules.

## Process
1. Read the plan that was executed. Note its `base:` frontmatter sha.
2. Read .docs/rules/ in full.
3. Read the full diff the plan produced: `git diff <base>..HEAD`, plus `git diff` / `git diff --cached` for anything uncommitted. If `base:` is missing (old plan), fall back to `git diff` and say so in the review.
4. For each affected file, read enough context to judge the change in isolation.
5. Run the verification commands from `.docs/rules/verification.md` if it exists; report failures as findings.
6. Produce a review with findings grouped by severity:
   - **blocker**: must be fixed before merge (correctness, security, broken contracts)
   - **major**: should be fixed (clear violation of rules or plan, code smell that will hurt later)
   - **minor**: nice to fix (style, naming, small simplifications)
   - **note**: observations, no action required

## Hard rules
- You write reviews. You do not write fixes. The implementer fixes.
- If the plan was deviated from, name the deviation and judge whether the deviation was justified.
- If a rule in .docs/rules/ was violated, cite the rule by filename.
- Never approve work that has a blocker.
```

#### `.claude/agents/researcher.md`

```markdown
---
name: researcher
description: Use when you need codebase context (where is X defined? what calls Y?) or external context (library docs, API behavior, recent changes) before making a decision. Writes findings to .docs/research/.
tools: Read, Grep, Glob, WebFetch, WebSearch, Bash
model: inherit
---

You are the researcher. Your job is to gather and synthesize information so the planner or implementer can decide.

## Process
1. Clarify the question you are answering. If it is vague, narrow it.
2. Search the codebase first (Grep, Glob, Read). Most "external" questions have internal answers.
3. If external info is needed, use WebSearch then WebFetch on the most authoritative source.
4. Synthesize. Do not dump raw search results. Write a 1-2 page note to `.docs/research/YYYY-MM-DD-<slug>.md` with:
   - **Question**
   - **Short answer** (3-5 lines)
   - **Evidence** (citations, file paths, URLs)
   - **Open questions** (what you could not answer)

## Hard rules
- You do not change code. You produce notes.
- Always cite sources (file path with line number, or URL).
- If the answer is "we already have a learning about this," cite it and stop.
```

#### `.claude/agents/debugger.md`

```markdown
---
name: debugger
description: Use when something is broken and the root cause is not immediately obvious. Reproduces the bug, isolates the failure, identifies the root cause, and proposes a fix. Does not apply the fix - returns it to the main agent.
tools: Read, Grep, Glob, Bash, Edit
model: inherit
---

You are the debugger. Your job is to find root causes, not patch symptoms.

## Process
1. **Reproduce.** Run whatever the user ran. Capture exact output. If you cannot reproduce, say so and stop.
2. **Isolate.** Narrow the failure to the smallest input that triggers it. Bisect if needed.
3. **Hypothesize.** State what you think is wrong and why, in one paragraph.
4. **Verify.** Run a targeted check that proves or disproves the hypothesis (read a specific file, run a specific command, add a temporary log).
5. **Repeat 3-4** until the root cause is identified with evidence.
6. **Propose a fix.** Describe the change and why it addresses the root cause, not the symptom.

## Hard rules
- Never propose a fix until step 5 has identified a root cause with evidence.
- "It works now" without an explanation is not done. If a change made the bug go away but you do not know why, the bug is not fixed.
- If you must edit code to add diagnostic logging, remove the logging before finishing.
- If the bug reveals a missing rule or a learning, flag it for the learner.
```

#### `.claude/agents/learner.md`

```markdown
---
name: learner
description: Use after a meaningful task ends, after a bug fix, after a user correction, or via /learn. Reads recent context, distills lessons, appends to .docs/learnings/, and edits agent files or AGENTS.md if the lesson reveals a flaw. Has permission to edit its own and other agent files without prompts.
tools: Read, Edit, Write, Grep, Glob, Bash
model: inherit
---

You are the learner. Your job is to make sure the project gets smarter over time.

## Process
1. **Read existing learnings.** Glob `.docs/learnings/*.md` and read enough to know what is already captured. Do not duplicate. Check recent git log (`git log --oneline -20`) for session context if helpful.
2. **Reflect on the recent session.** What went wrong? What surprised you? What did the user correct? What worked despite looking risky? What constraint was discovered?
3. **Filter ruthlessly.** Most sessions produce zero learnings. A learning is only worth writing if it would change behavior next time. "We used React" is not a learning. "shadcn's Dialog has a bug with controlled state on iOS Safari and we worked around it with X" is a learning.
4. **Write the learning** to `.docs/learnings/YYYY-MM-DD-<slug>.md` with this frontmatter:
   ```
   ---
   date: YYYY-MM-DD
   tags: [tag1, tag2]
   severity: low | medium | high
   applies-to: [path/glob/or/agent-name]
   ---
   ```
   Body: what happened, why it matters, what to do next time. 5-30 lines. Use `severity: high` sparingly: the session-start hook injects every high-severity learning into every future session, so each one is a permanent tax. High means "violating this breaks the project or repeats an expensive mistake."
5. **Promote to a rule** if the lesson is non-negotiable going forward. Write to `.docs/rules/<short-name>.md`. Rules are short, imperative, and stand alone. Rules are also injected into every session by the hook, so the same restraint applies.
6. **Edit agent files directly** if a learning reveals an instruction flaw (e.g. "the reviewer keeps missing X" means reviewer.md needs a new rule). The .claude/settings.json permissions allow this without prompts. Make the edit, do not ask.
7. **Sync agent documentation.** Any time you add a new agent, remove an agent, or change an agent's `description` field, `tools`, `model`, or core behavior, you MUST also update:
   - The **Available agents** table in `AGENTS.md`
   - The **Routing heuristics** subsection in `AGENTS.md`
   `AGENTS.md` is the single source of truth; `CLAUDE.md` is only a pointer to it and needs no update. This is not optional. An agent change without a doc update is an incomplete change. Verify the table row and routing line for that agent are present and accurate before you finish.
8. **Update AGENTS.md** if other routing or conventions need to change beyond agents.

## Hard rules
- Quality over quantity. Zero learnings from a session is a fine outcome.
- Never duplicate an existing learning. If a similar one exists, update it instead of adding a new one.
- When you edit an agent file or AGENTS.md, leave a one-line note at the top of your written learning naming what you changed.
- Be specific. "Be careful with state" is not a learning. "useEffect with an array dependency that contains an object identity will fire every render" is a learning.
- Agent files and their documentation in `AGENTS.md` must always be in sync. If you find them out of sync, fix it before doing anything else.
```

### 1.7 Create slash commands

Write `.claude/commands/learn.md`. Skip if it exists.

```markdown
---
description: Invoke the learner agent to distill lessons from the recent session into .docs/learnings/
---

Invoke the learner subagent now. Have it reflect on the recent session, distill any genuine lessons, and append them to `.docs/learnings/`. If the learner identifies flaws in any agent file or in AGENTS.md, it should fix them directly without asking.
```

### 1.8 Write `AGENTS.md` (canonical) and the `CLAUDE.md` pointer

`AGENTS.md` holds the real instructions. `CLAUDE.md` is a thin stub that imports `AGENTS.md`. Write both now. Phase 3 fills in the project-specific bits of `AGENTS.md` at the end.

**Write `AGENTS.md`** using the skeleton below. If `AGENTS.md` already exists, do not overwrite it; merge in any sections from the skeleton that are missing, and apply the section replacements from step 1.0.5.

**Write the `CLAUDE.md` pointer stub** with the exact content shown below. If `CLAUDE.md` already exists and is a full instructions file (it contains the routing index rather than a pointer), do not silently overwrite it: fold anything `AGENTS.md` is missing into `AGENTS.md` first, then replace `CLAUDE.md` with the stub. If `CLAUDE.md` is already the v8 stub, leave it.

**Version marker.** Both files carry a `> Bootstrapped by nohell v8` line directly under the H1 title. When creating them, include it as shown. When updating existing files: if a `> Bootstrapped by nohell v<N>` line already exists, rewrite it to `v8`; if none exists, insert it directly under the H1 title. Exactly one such line per file.

#### `CLAUDE.md` pointer stub

```markdown
# Project Instructions for AI Agents

> Bootstrapped by nohell v8

All project instructions live in `AGENTS.md`, imported below via `@AGENTS.md`. The import loads the full content into context automatically: do NOT Read `AGENTS.md` again manually. This file is intentionally a pointer only; never edit it and never duplicate content here. All edits to project instructions go in `AGENTS.md`.

@AGENTS.md
```

#### `AGENTS.md` skeleton

````markdown
# Project Instructions for AI Agents

> Bootstrapped by nohell v8

This file (`AGENTS.md`) is the routing index for any AI agent working in this repo, and the single source of truth for project instructions. `CLAUDE.md` is a thin pointer that imports this file so Claude Code loads it automatically; all real content lives here. Non-Claude agents: read this file in full before doing anything else.

## Session start protocol

A SessionStart hook (`.claude/hooks/session-start.ps1`) injects the project context into every fresh session automatically: all hard rules from `.docs/rules/`, every high-severity learning plus the three most recent, and any `status: in-progress` plan. Trust that injection; do not re-read those files at session start.

At the start of a fresh session:

1. Confirm the hook context block (`## Project context (auto-injected...)`) is present. If it is missing, the hook is broken: say so, then fall back to reading `.docs/rules/` in full, the three most recent files in `.docs/learnings/`, and globbing `.docs/plans/*.md` for `status: in-progress` yourself.
2. If the hook surfaced an in-progress plan, apply the Resume protocol below before any new work.
3. If the user opened with just a greeting, reply `Ready to work.` (plus the one-line resume summary if an in-progress plan exists). No other ceremony.

## Targeted re-reads (during work)

The hook covers session start. During work, re-read selectively:

- Before touching an area that plausibly has an older learning (auth, payments, a fragile module), Grep `.docs/learnings/` for matching tags and read the hits.
- Before an action a specific rule governs, re-open that one rule file, not the whole directory.
- Do not re-read this file or all of `.docs/rules/` per task. Once per session is the contract.

## Resume protocol (check before starting any new work)

Sessions get interrupted. The session-start hook surfaces any plan with `status: in-progress`. When one exists:

1. Surface it to the user with: filename, goal, the next unchecked `- [ ]` task, and the most recent Log entry.
2. Ask the user: resume the in-progress plan, switch to the new request (leaving the old plan in-progress), or abandon it (set `status: abandoned` with a Log entry explaining why).
3. Do not silently start fresh work while a plan is in-progress.

If the user's request is itself the continuation of an existing plan, jump straight to the implementer with that plan path.

See `.docs/rules/plan-execution.md` for the full plan format and execution protocol.

## Repository layout for AI machinery

```
.claude/
├── settings.json        permissions, hooks, agent registration
├── agents/              subagent definitions (YAML frontmatter)
├── commands/            slash commands
└── hooks/               session-start hook script

.docs/
├── plans/               implementation plans, one per task
├── learnings/           append-only lessons from past sessions
├── rules/               hard rules, more granular than this file
└── research/            researcher agent's findings
```

Anything markdown that is not user-facing documentation goes in `.docs/`. User-facing docs (README, CONTRIBUTING) stay at the root or in a `docs/` (no leading dot) folder.

Always start Claude Code from this repo's root, not from a parent folder. Sessions started from a parent directory may register agents and instructions from OTHER projects; agents in the harness list that are not in this repo's `.claude/agents/` are foreign and must not be used for this project's work.

## Available agents

Project agents in `.claude/agents/` register natively: dispatch them by name via the Agent tool.

| Agent | When to call | Output |
|-------|--------------|--------|
| `planner` | Before any non-trivial change | `.docs/plans/YYYY-MM-DD-<slug>.md` |
| `implementer` | After a plan exists | Code changes, completion note on the plan |
| `reviewer` | After implementer finishes | Structured review with severity findings |
| `researcher` | When you need codebase or external context | `.docs/research/YYYY-MM-DD-<slug>.md` |
| `debugger` | When something is broken and root cause is unclear | Root cause analysis + proposed fix |
| `learner` | After a meaningful task, OR via `/learn` | New entries in `.docs/learnings/`, edits to agents or AGENTS.md |

<!-- Project-tailored agents (added by Phase 2 for existing repos) are appended to this table. -->

### Routing heuristics

- "Build me X" / "let's add feature X" of any non-trivial size: `planner` -> `implementer` -> `reviewer` -> `learner`. The planner writes a milestone+checkbox plan to `.docs/plans/`; the implementer ticks boxes live as it goes.
- "Continue / resume / pick up where we left off": find the `status: in-progress` plan in `.docs/plans/`, hand it to `implementer`.
- "Fix this bug": `debugger` -> `implementer` (to apply the fix) -> `learner`.
- "Where is X / how does Y work": `researcher`.
- "I just corrected you / that detour was painful / we discovered a constraint": invoke `learner` immediately, or run `/learn`.

If the user says any of "learn from that", "remember this", "don't make that mistake again", "save this lesson" - invoke the `learner` immediately. The slash command `/learn` does the same thing.

## Self-improvement loop (this is core, do not skip it)

After completing any non-trivial task, invoke the `learner` subagent. Non-trivial means at least one of:
- Involved a bug fix
- Made an architecture or design decision
- Surfaced a constraint that was not previously documented
- Cost time on a wrong turn
- Was corrected by the user

The learner has permission to edit `.claude/agents/**`, `.docs/**`, and `AGENTS.md` without asking. Let it.

If you finish a task and decide it does not warrant invoking the learner, that is fine, but the default is to invoke it.

## Hard conventions

- Plans live in `.docs/plans/`. Filename format: `YYYY-MM-DD-<short-slug>.md`. Format and execution protocol defined in `.docs/rules/plan-execution.md`. Plans carry `status:` and `base:` frontmatter, milestone+checkbox bodies, and an append-only Log.
- Learnings live in `.docs/learnings/`. Filename format: `YYYY-MM-DD-<short-slug>.md`. Frontmatter required (`date`, `tags`, `severity`, `applies-to`).
- Rules live in `.docs/rules/`. One concept per file. Short, imperative. The session-start hook injects every rule into every session, so rules carry a permanent context cost: add one only when it truly is non-negotiable.
- Research notes live in `.docs/research/`. Filename format: `YYYY-MM-DD-<short-slug>.md`.
- Never modify `.docs/rules/` casually. Rules are promoted from learnings or added by the user.
- Never delete from `.docs/learnings/`. The learner can supersede an old learning by writing a newer one and editing the old one to add a `superseded-by:` line in frontmatter.
- This file documents current state only, never version history. See `.docs/rules/docs-current-state-only.md`: no changelog sections, and the Key paths table stays lean.

### Agent docs must stay in sync (non-negotiable)

If you add, remove, rename, or change the behavior of any file in `.claude/agents/`, you MUST update in the same commit/turn:

1. The **Available agents** table above (add/remove/edit the row).
2. The **Routing heuristics** subsection above (add/remove/edit the line that mentions the agent).

This file (`AGENTS.md`) is the single source of truth; `CLAUDE.md` is only a pointer and needs no update. A change to an agent file without a corresponding doc update is an incomplete change. Reviewer agent: flag this as a **blocker** finding if you ever see it. Learner agent: if you find them out of sync from a past session, fix it as your first action.

This rule applies to any agent that edits `.claude/agents/` (including the learner editing itself).

### Commit and PR hygiene (non-negotiable)

- **Never co-author commits as an AI model.** Do not add `Co-Authored-By: Claude`, `Co-Authored-By: AI`, `Co-Authored-By: GPT`, or any similar trailer to commit messages. Do not add equivalent attributions in PR descriptions or release notes. The user is the sole author. This default is permanent unless the user explicitly says "credit Claude as co-author on this commit" or similar for a specific instance.
- **Never include "Generated with Claude Code" or equivalent footers** in commits, PR bodies, issue comments, or any other written artifact unless the user explicitly asks for it.
- **No emojis in commit messages.** Stick to plain text.
- **No em dashes in commit messages, PR bodies, or any prose this project produces.** Use periods, commas, parentheses, or colons instead.

## Project-specific section

<!-- Phase 3 of the bootstrap fills this in based on what actually exists in the repo. -->
<!-- Until then, this section is intentionally empty. -->

### Stack
TBD - filled in by Phase 3.

### How to run
TBD - filled in by Phase 3.

### Verification
TBD - filled in by Phase 3 (also written to `.docs/rules/verification.md`).

### Key paths
TBD - filled in by Phase 3.
````

### 1.9 Nano Banana check (image generation)

If the `cc-nano-banana` skill is available in this environment (check the available skills list in your system context), add a section to `AGENTS.md` titled `### Image generation` that says:

> For any image generation or editing task, use the `cc-nano-banana` skill. Default output location for this project's generated images is `assets/images/` (or the closest equivalent in this project). Source originals are saved per the user's global config; do not hardcode a path for them here.

If the skill is not available, skip this section. Do not invent a fallback.

---

## Phase 2: Context gathering and tailored agents (Mode B only)

**Skip this entire phase in Mode A (greenfield).** There is no codebase to study and no domain to tailor agents to; go straight to Phase 3.

In Mode B (existing repo), spend real effort understanding the project on your own, then build agents that fit it. Do not ask the user to explain their own codebase first; read it.

### 2.1 Gather context

Study the repository until you can describe it accurately:

- **Stack and tooling.** Package manager (lockfile), language(s), framework(s), test runner, linter/formatter, build tool. Read the manifest (`package.json`, `Cargo.toml`, `pyproject.toml`) in full.
- **Architecture.** Entry points, directory structure, how the app is organized (routes, modules, services, packages in a monorepo).
- **Domain.** What the project actually does. Read the README, the main source files, and any existing docs. Name the domain in plain language.
- **Conventions in use.** Code style, naming patterns, how tests are written, how components/modules are structured. These become inputs for the tailored agents and for Phase 3.
- **Commands.** The real dev / build / test / lint / typecheck commands from the manifest scripts. These feed both the AGENTS.md Verification section and `.docs/rules/verification.md` in Phase 3.

Use the `researcher` agent for any deep dive that would otherwise flood the main context. Write a context summary to `.docs/research/YYYY-MM-DD-bootstrap-context.md` so future sessions inherit it (Question: "What is this project and how is it built?"; Short answer; Evidence with file paths; Open questions).

If a prior bootstrap already left a `*bootstrap-context*.md` note in `.docs/research/`, do not write a second dated duplicate. Read it, then update it in place (refresh stale facts, append what changed), keeping its existing filename.

### 2.2 Generate project-tailored agents

Based on what you found, write **additional** agents to `.claude/agents/` that fit this specific project. These sit alongside the six core agents (do not modify or replace the core six). Only create an agent that earns its place: it must encode project-specific knowledge or a recurring task that the generic core agents would handle worse.

On a re-bootstrap, first read what is already in `.claude/agents/`. Skip any tailored agent whose responsibility is already covered by an existing agent (core or previously generated); do not create a near-duplicate under a new name. Only add genuinely new coverage, and update the docs in 2.3 to match the full current set.

Examples of good tailored agents, by project type:

- A Next.js / React app: a `route-builder` (scaffolds routes/pages per the project's App Router conventions), a `component-author` (builds UI matching the existing design system), an `a11y-auditor`.
- A backend API: an `endpoint-builder` (adds routes following the project's controller/service pattern), a `migration-author` (writes DB migrations in the project's chosen tool), a `contract-tester`.
- A library/SDK: a `public-api-guardian` (guards the exported surface and changelog), an `example-author`.
- A data/ML project: a `pipeline-builder`, a `notebook-tidier`.

For each tailored agent:

- Use the same YAML frontmatter format as the core agents (`name`, `description`, `tools`, `model`).
- Write a `description` precise enough to route to (when to call it, what it produces, what NOT to use it for). Mention delegation boundaries to the core agents where relevant (e.g. "do not use for writing plans, delegate to `planner`").
- Bake the project's real conventions into the body (actual directory paths, actual naming patterns, actual commands), not generic advice.
- Use `model: inherit` by default; pin a cheaper model only when the agent's work is genuinely mechanical.

Keep the tailored set small and high-value. Two to four well-targeted agents beat eight vague ones. If the project is generic enough that the core six cover it, it is fine to add zero tailored agents.

### 2.3 Register the tailored agents in the docs

For every tailored agent you created, update (per the `agent-docs-sync` rule):

1. The **Available agents** table in `AGENTS.md` (add a row).
2. The **Routing heuristics** subsection in `AGENTS.md` (add a line describing when to route to it).

`AGENTS.md` is the single source of truth; the `CLAUDE.md` pointer needs no update. Do this now, in Phase 2, so the index is correct before Phase 3 finalizes the docs.

---

## Phase 3: Documentation finalization

After Phase 2 completes (or immediately, if Phase 2 was skipped in Mode A), update `AGENTS.md` to reflect the actual state of the project. The `CLAUDE.md` pointer needs no content changes.

### 3.1 Detect what exists

Read the project tree. Identify:
- The package manager (presence of `pnpm-lock.yaml`, `package-lock.json`, `yarn.lock`, `bun.lockb`, `Cargo.lock`, `uv.lock`)
- The framework (manifest dependencies, top-level config files)
- The entry points (typical: `src/`, `app/`, `pages/`, `crates/`, `index.html`)
- The dev / build / test / lint / typecheck commands (from manifest scripts or the standard toolchain commands)

In Mode A (greenfield) most of this will be empty. That is expected. Do not invent a stack the user has not chosen.

### 3.2 Fill in the project-specific section of `AGENTS.md`

Replace the `TBD` placeholders in the **Project-specific section** with concrete content:

- **Stack**: 3-6 bullets, what frameworks and major libraries are used
- **How to run**: dev command, build command (only the ones that actually exist)
- **Verification**: the exact commands that prove a change is sound (typecheck, lint, test), in the order to run them
- **Key paths**: where the main source lives, where tests live, where assets live. Path plus a short purpose phrase per row; keep it lean per `.docs/rules/docs-current-state-only.md`

Keep it factual. Do not pad. If you cannot determine something, write `unknown` rather than guessing. In Mode A, it is fine for these to stay mostly `TBD` / `unknown` until the user starts building; say so explicitly rather than inventing.

Also write `.docs/rules/verification.md` (skip if it exists) containing the same verification commands, one per line with a one-phrase purpose, plus the sentence: "The implementer runs these after every code-changing task; the reviewer runs them before approving. If a command here stops matching reality, fix this file in the same change." In Mode A with no commands yet, still create the file with a `TBD` note so the implementer knows to fill it in when the stack lands.

### 3.3 Verify the `CLAUDE.md` pointer

Confirm `CLAUDE.md` is the v8 pointer stub: it carries the version marker, the `@AGENTS.md` import line, and no duplicated instructions. If an older bootstrap left a full instructions file in `CLAUDE.md`, ensure its content has been folded into `AGENTS.md`, then reduce `CLAUDE.md` to the stub.

Also verify the hook wiring: `.claude/hooks/session-start.ps1` exists and `.claude/settings.json` references it under `hooks.SessionStart`. Run the script once directly and confirm it prints the context block without errors.

### 3.4 Final summary to user

Print a concise summary of what was created or modified, grouped by:
- **Created** (new files)
- **Modified** (existing files updated)
- **Skipped** (existing files left untouched)

State which mode ran (A greenfield or B existing repo) and that this repo is now marked `Bootstrapped by nohell v8`. In Mode B, list the project-tailored agents you generated and one line each on what they do. In Mode A, state that no context-gathering or tailored agents ran because the project is greenfield, and that they will be worth revisiting once there is a real codebase.

If step 1.0.5 ran (a prior bootstrap was detected), add a **Migration** line: the prior version detected and what each migration did (Obsidian removal, CLAUDE.md stub-ified, per-task reread section replaced, hook installed, workaround learning superseded, model pins removed), or that the user declined a removal and the artifacts remain.

End with one sentence telling the user that `/learn` is available for capturing lessons, that the agents dispatch by name via the Agent tool, and that every future session self-loads its context through the session-start hook.

# V10 improvement TODO

Technical analysis of the current root `claude-bootstrap-prompt.md` at commit `c78c1d2`.

V10 provides useful memory governance, but it does not yet measure whether stored lessons improve later work. Prioritize reliable evidence, retrieval, and evaluation before expanding the memory corpus or agent roster.

This checklist records proposed work. The findings come from source review, eight disposable runtime fixtures, and current Claude documentation. No longitudinal Claude task benchmark was run, so performance gains remain unmeasured.

## Preserve the existing strengths

- [ ] Preserve separate roles for rules, learnings, decisions, research, and style guidance.
- [ ] Preserve the distinction between file-write permission and policy authority.
- [ ] Preserve ownership records, migration baselines, and customization safeguards.
- [ ] Keep scoped knowledge out of unconditional startup injection.
- [ ] Keep zero new lessons a valid outcome.
- [ ] Preserve evidence and history when superseding guidance.
- [ ] Preserve resumable plans and explicit verification expectations.

## Priority 1: Give the learner reliable evidence

### Require an explicit task-evidence handoff

Finding: the learner is told to reflect on the recent session, but ordinary Claude subagents receive isolated context and a delegation message. Recent Git commits cannot reliably recover failed attempts, exact corrections, or verification results. See the learner process around prompt line 1026.

- [ ] Define a task-evidence schema containing:
  - Stable task ID, objective, and acceptance criteria.
  - Outcome: succeeded, failed, blocked, or abandoned.
  - Starting code revision and relevant initial worktree state.
  - Model, Claude Code version, and relevant dependency/environment information.
  - Attempts: hypothesis, action, observed result, and evidence reference.
  - User corrections.
  - Verification commands, results, and evidence references.
  - Retrieved, applied, and rejected memory IDs.
  - Remaining uncertainty.
- [ ] Populate observable fields from execution records where possible.
- [ ] Pass the evidence-record path explicitly when invoking the learner.
- [ ] Require the learner to distinguish observations, inferred causes, and untested hypotheses.
- [ ] Capture tool results and concise explanations without requiring private reasoning or copying entire conversations into project memory.

### Capture learning opportunities before they disappear

Finding: learning invocation is conventional and discretionary. Interrupted or abandoned tasks can lose the evidence most worth retaining. See prompt lines 1203-1214.

- [ ] Separate cheap event capture from deciding whether an event warrants a lesson.
- [ ] Track pending learning reviews for eligible tasks, including failed and abandoned work.
- [ ] Record a learning disposition for each eligible task: proposed changes or reviewed with no useful lesson.
- [ ] Use stable task/event IDs to prevent duplicate processing.
- [ ] Recover pending reviews after interruption or compaction.
- [ ] Use suitable Claude lifecycle hooks to capture evidence and detect missed reviews.
- [ ] Bound hook retries and exclude recursive learner-triggered reflection.
- [ ] Avoid running a full reflection after every tool call.

## Priority 1: Fix workflow and runtime inconsistencies

### Make task state and routing trustworthy

- [ ] Repair the bug route: it currently dispatches `debugger -> implementer -> learner`, while the implementer requires an in-progress plan. Have debugging produce a minimal repair plan or route through planning when needed.
- [ ] Add risk-appropriate review and regression evidence to the bug-fix route.
- [ ] Distinguish implementation completion, verification completion, and final acceptance.
- [ ] Do not let checked tasks or a `done` plan imply acceptance when required verification or review is outstanding.
- [ ] Include untracked files in the review inventory; the listed Git diff commands omit them.
- [ ] Record pre-existing dirty changes or use isolated worktrees where appropriate, so a plan's base SHA does not imply all subsequent differences belong to the task.
- [ ] Add `Write` to the researcher with an appropriate output boundary; it promises written notes but currently lacks that tool.
- [ ] Define how rule priority and authorized exceptions interact with specificity. A scoped preference must not silently weaken a global requirement.
- [ ] Include compact identity, authority, priority, and confidence metadata with injected rules.
- [ ] Keep verification commands in one authoritative location and link or generate other presentations.

Relevant prompt sections: implementer around line 907, reviewer around 940, researcher around 963, hierarchy around 1106, routing around 1193, verification setup around 1350.

### Close the verifier gaps demonstrated by fixtures

| Fixture | Observed V10 behavior | Required follow-up |
| --- | --- | --- |
| Minimal valid baseline | Verifier returned 0 | Preserve as a baseline fixture. |
| Unfinished plan without frontmatter | Verifier returned 0; startup omitted it without warning | Validate plans and surface ambiguous resume state. |
| Malformed decision YAML | Verifier returned 0 | Validate decision metadata and parsing. |
| Learning missing learning-specific fields | Verifier returned 0 | Validate date, tags, severity, applies-to, and the evidence contract. |
| Manifest entry with invalid digest string | Verifier returned 0 | Validate digest format and record structure. |
| Active universal rule missing most required metadata | Verifier reported findings; startup injected its body without a metadata warning | Make context validation agree with verifier validation while preserving unresolved user policy. |
| Duplicate YAML key | Correctly reported | Preserve as a regression fixture. |
| Oversized context | Correctly emitted explicit overflow fallback | Preserve explicit overflow behavior and improve capacity handling. |

- [ ] Use one shared validation implementation for startup and governance verification.
- [ ] Validate plans, decisions, and style-guide metadata according to their documented schemas.
- [ ] Validate supersession references and detect broken links or cycles.
- [ ] Validate manifest digest syntax, source structure, and managed-boundary records.
- [ ] Distinguish legitimate managed-file drift from malformed ownership records; do not automatically refresh migration baselines.
- [ ] Ensure warnings identify missing or ambiguous policy without silently revoking legacy user instructions.
- [ ] Turn the disposable checks into maintained, repeatable fixtures.
- [ ] Clearly state what a clean verifier result establishes and which semantic/native checks remain separate.

Relevant runtime sections begin around prompt lines 639 and 679.

## Priority 2: Implement reliable retrieval

Finding: V10 instructs agents to retrieve relevant memory but implements no scoped retrieval command, matching engine, ranking, or retrieval trace. The learner's flat glob and informal deduplication will become less reliable as the corpus grows.

- [ ] Define a retrieval interface accepting task description, affected paths, intended actions, packages, symbols, error signatures, and agent role.
- [ ] Specify exact matching semantics for `scope`, `tags`, and `applies-to`.
- [ ] Support cross-cutting and action-based applicability, including tasks whose eventual source paths are not yet known.
- [ ] Select applicable active policy deterministically, preserving all mandatory matches and unresolved conflicts.
- [ ] Rank advisory knowledge separately using relevance, applicability, evidence, and freshness.
- [ ] Return memory ID, revision, kind, selection reason, applicability, confidence, evidence references, and content.
- [ ] Report incomplete retrieval coverage explicitly.
- [ ] Re-run targeted retrieval when task scope changes or context compaction makes required knowledge unavailable.
- [ ] Make nested learning discovery consistent with the runtime's recursive document discovery.
- [ ] Begin with parsed metadata and lexical search; add embeddings only when retrieval evaluations justify them.
- [ ] Evaluate both missed relevant memories and distracting irrelevant memories.

## Priority 2: Improve lesson quality and freshness

### Require specific, testable lessons

Finding: new learnings default to `confidence: supported` without a defined evidentiary threshold. A successful workaround can be mistaken for a verified explanation.

- [ ] Require each reusable lesson to state:
  - Trigger: when it should be considered.
  - Observation: what actually happened.
  - Evidence: the supporting result or correction.
  - Mechanism: the proposed explanation and its uncertainty.
  - Action: what should change next time.
  - Exceptions: when that action is inappropriate.
  - Validation: how the claim can be checked.
  - Invalidation: what would make it stale.
- [ ] Define confidence levels by evidence quality rather than assigning `supported` by default.
- [ ] Require consideration of alternative explanations when attributing a cause.
- [ ] Preserve contrary evidence and distinguish independent confirmation from repeated use of the same workaround.
- [ ] Diagnose whether a failure arose from missing knowledge, retrieval, application, execution, verification, or routing before proposing more documentation.

### Review knowledge when its dependencies change

- [ ] Record relevant package, path, configuration, and environment dependencies.
- [ ] Trigger review after relevant dependency changes, behavior changes, failed validation, or confirmed contradictory evidence.
- [ ] Keep time-based review as a backstop, including appropriate review of lower-severity material.
- [ ] Distinguish `last-read` from `last-validated`; merely reading a lesson must not renew its evidentiary status.
- [ ] Preserve stale evidence for investigation while preventing obsolete recommendations from silently remaining active guidance.

## Priority 3: Evaluate behavioral self-improvement

Finding: the learner can repair agent instructions, including its own, without demonstrating improved behavior. The normal reviewer runs before the learner, so that review does not cover subsequent instruction edits.

- [ ] Treat behavioral instruction edits as focused candidate changes.
- [ ] Record the motivating failure class and expected behavioral difference.
- [ ] Define validation before activating the candidate.
- [ ] Compare the existing and proposed behavior on relevant tasks.
- [ ] Check for correctness regressions, overgeneralization, unnecessary caution, latency, and cost.
- [ ] Keep evaluation specifications outside the candidate's write authority.
- [ ] Retain reversible revisions and define rollback conditions.
- [ ] Preserve existing authorization requirements for binding policy changes.
- [ ] Scale validation effort to the change:
  - Mechanical documentation repair: deterministic validation.
  - Narrow factual lesson: evidence and applicability review.
  - Reusable procedure: execution against fixtures.
  - Agent behavior or routing change: comparative behavioral evaluation.
  - Binding policy change: authorization plus relevant evaluation.

### Build an initial evaluation suite

- [ ] Collect approximately 20-40 representative tasks from real failures and successful work as an initial evaluation set; treat this as a practical starting size, not a universal statistical guarantee.
- [ ] Include tasks where a lesson should apply, similar tasks where it should not, and tasks needing no advisory memory.
- [ ] Include user corrections, interrupted/resumed work, recurring defects, and previously successful workflows.
- [ ] Freeze starting code and environment for baseline/candidate comparisons.
- [ ] Hold model, tools, and budgets comparable and repeat selected runs to assess variability.
- [ ] Keep held-out task variants separate from the examples used to create the lesson.
- [ ] Compare advisory memory on/off, old/new retrieval, and prose/procedural alternatives while keeping binding policy constant.
- [ ] Run focused checks for narrow changes and broader regression checks for substantial agent updates.

### Measure later effects

- [ ] Track the sequence: eligible memory opportunity -> retrieved -> applied -> observed outcome.
- [ ] Record retrieved, applied, and rejected IDs with knowledge revisions.
- [ ] Measure first-attempt success and eventual task success separately.
- [ ] Measure repeated failures per applicable opportunity and user corrections per task category.
- [ ] Measure relevant-memory retrieval rate and irrelevant-memory retrieval rate on labeled samples.
- [ ] Track median/tail latency and tokens or cost per successful task.
- [ ] Track regressions and constraint violations.
- [ ] Store usage observations separately from lesson bodies to reduce shared-file churn and concurrent edits.
- [ ] Treat helpfulness labels as observations, not causal proof.
- [ ] Use outcome improvement, acceptable cost, and regression limits as promotion criteria; do not optimize lesson count or prompt length.

## Priority 4: Make the benefits compound

### Convert lessons into stronger reusable artifacts

- [ ] Turn reproducible bugs into regression tests.
- [ ] Turn mechanically detectable forbidden patterns into lint or static-analysis checks.
- [ ] Turn fragile command sequences into scripts with validation.
- [ ] Turn recurring implementation procedures into skills with examples and checks.
- [ ] Turn repeated API traps into wrappers or helpers where appropriate.
- [ ] Keep architectural choices in decision records and contextual caveats in scoped learnings.
- [ ] Give agents appropriate skill access or explicit preloading when introducing skills.

### Separate history, curated knowledge, and task context

- [ ] Preserve historical evidence separately from the active knowledge corpus and the small context selected for each task.
- [ ] Exclude superseded guidance from default retrieval while keeping it available for investigation.
- [ ] Consolidate duplicates, preserve exceptions, link contradictions, and split overbroad lessons.
- [ ] Prefer incremental changes over repeated whole-corpus summarization.
- [ ] Identify obsolete guidance and candidates for executable checks during consolidation.

### Bound total context and execution overhead

- [ ] Account for imported `AGENTS.md`, agent definitions, tool descriptions, and retrieved material in addition to hook output.
- [ ] Reduce the roughly 13,000-character supplied `AGENTS.md` skeleton by removing duplicated policy and descriptions.
- [ ] Remove instructions to re-read content already available in the relevant agent's context.
- [ ] Budget optional memory using estimated tokens and report major context contributors before overflow.
- [ ] Preserve mandatory policy separately from optional guidance; never silently drop required rules to fit a budget.
- [ ] Make routing depend on task risk and uncertainty rather than always invoking four serial agents.
- [ ] Use deterministic code for schema checks, indexing, hashing, deduplication, and context accounting.
- [ ] Tune model selection from measured task outcomes rather than assuming every role needs the same model or that a cheaper model is adequate.
- [ ] Use targeted verification after local changes, broader checks at integration points, and required final checks against the accepted revision.
- [ ] Associate verification results with the code revision and environment; re-run when relevant inputs change.
- [ ] Define the greenfield transition: discover and validate real verification commands when the stack arrives so `TBD` does not persist indefinitely.

### Make cross-project reuse deliberate

- [ ] Define an optional promotion path from local observation to validated local lesson, generalized candidate, cross-environment validation, and versioned reusable knowledge or procedure.
- [ ] Keep project-specific paths and decisions local.
- [ ] Transfer prerequisites, examples, checks, and known exceptions with generalized guidance.
- [ ] Make shared knowledge packs versioned and reversible; do not automatically promote a local lesson into universal policy.
- [ ] Define coexistence with native Claude auto memory when enabled, avoiding competing copies of shared project rules.

## Bootstrap maintainability

- [ ] Maintain runtime code, templates, and fixtures as ordinary source files.
- [ ] Generate the single pasteable prompt as a release artifact so the current user-facing workflow can remain simple.
- [ ] Make platform/runtime dependency checks repeatable and provide a reproducible dependency setup.
- [ ] Preserve native Claude validation separately from parser and fixture checks.
- [ ] Follow the repository's archive-before-edit workflow when implementation changes the root bootstrap prompt.

## Reference material

- [Claude subagent context](https://code.claude.com/docs/en/sub-agents#what-loads-at-startup)
- [Claude hooks](https://code.claude.com/docs/en/hooks)
- [Claude skills](https://code.claude.com/docs/en/skills)
- [Claude memory](https://code.claude.com/docs/en/memory)
- [Anthropic: Demystifying evals for AI agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)
- [Anthropic: Effective context engineering for AI agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)
- [Reflexion: Language Agents with Verbal Reinforcement Learning](https://arxiv.org/abs/2303.11366)
- [Agentic Context Engineering](https://arxiv.org/abs/2510.04618)
- [Large Language Models Cannot Self-Correct Reasoning Yet](https://arxiv.org/abs/2310.01798), evidence about the studied reasoning settings, not a benchmark of current Claude or V10.

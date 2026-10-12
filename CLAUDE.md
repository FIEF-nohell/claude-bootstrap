# Maintenance instructions

This repo holds a single prompt file, `claude-bootstrap-prompt.md`, that is iterated on over time, plus tests for the Python helper embedded in it. Older versions are archived in `old-versions/`.

## Versioning workflow (mandatory before every edit)

When the user asks for a change to `claude-bootstrap-prompt.md`, follow this exact sequence:

1. **List `old-versions/`.** Find the highest existing `claude-bootstrap-prompt-vN.md` filename. The next version number is `N+1`. If the folder is empty (ignoring any README), the next version number is `1`.

2. **Copy the current root file into the archive** before making any edits:
   - From: `claude-bootstrap-prompt.md`
   - To: `old-versions/claude-bootstrap-prompt-v<N+1>.md`
   - Use a copy operation, not a move. The root file must remain in place.

3. **Edit the root `claude-bootstrap-prompt.md`** with the requested changes.

4. **Keep the release metadata in step.** Bump `bootstrap-release.json` and the README (status line and a new `### v<N>` section under "Bootstrap update details") to the new prompt version, and add the matching migration in step 1.0.5 of the prompt.

5. **Run the tests** (`python3 -m unittest discover -s tests`; needs PyYAML). They extract the embedded helper from the prompt and run it against disposable fixtures, and `tests/test_release.py` fails when version strings disagree.

6. **Confirm to the user** which version was archived, that the root file now contains the new version, and the test result.

## Rules

- Never edit the root file without first archiving it. If you forget, the previous version is lost.
- Never edit files inside `old-versions/`. They are immutable history.
- Version numbers only ever increase. Do not renumber, do not reuse numbers, do not skip numbers.
- The archive filename pattern is exactly `claude-bootstrap-prompt-v<N>.md`. No date, no slug, no other suffix.
- If the user requests a small change (a typo fix, a one-line tweak), still archive first. There is no "too small to version" exception. Disk is cheap.

## What this repo is not

This repo is the **maintenance environment for the prompt itself**. It is not a project that uses the prompt. The prompt is a deliverable that gets pasted into other Claude sessions. Do not try to "bootstrap" this repo with the prompt's own instructions.

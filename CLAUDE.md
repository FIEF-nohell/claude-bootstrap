# Maintenance instructions

This repo holds a single prompt file, `claude-bootstrap-prompt.md`, that is iterated on over time. Older versions are archived in `old-versions/`.

## Versioning workflow (mandatory before every edit)

When the user asks for a change to `claude-bootstrap-prompt.md`, follow this exact sequence:

1. **List `old-versions/`.** Find the highest existing `claude-bootstrap-prompt-vN.md` filename. The next version number is `N+1`. If the folder is empty (ignoring any README), the next version number is `1`.

2. **Copy the current root file into the archive** before making any edits:
   - From: `claude-bootstrap-prompt.md`
   - To: `old-versions/claude-bootstrap-prompt-v<N+1>.md`
   - Use a copy operation, not a move. The root file must remain in place.

3. **Edit the root `claude-bootstrap-prompt.md`** with the requested changes.

4. **Confirm to the user** which version was archived and that the root file now contains the new version.

## Rules

- Never edit the root file without first archiving it. If you forget, the previous version is lost.
- Never edit files inside `old-versions/`. They are immutable history.
- Version numbers only ever increase. Do not renumber, do not reuse numbers, do not skip numbers.
- The archive filename pattern is exactly `claude-bootstrap-prompt-v<N>.md`. No date, no slug, no other suffix.
- If the user requests a small change (a typo fix, a one-line tweak), still archive first. There is no "too small to version" exception. Disk is cheap.

## What this repo is not

This repo is the **maintenance environment for the prompt itself**. It is not a project that uses the prompt. The prompt is a deliverable that gets pasted into other Claude sessions. Do not try to "bootstrap" this repo with the prompt's own instructions.

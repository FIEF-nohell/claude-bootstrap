---
description: Activate the remote design-studio module and create or revise the project's living design system
---

Run the installed `design-studio` module workflow. Read `.claude/modules/design-studio/manifest.json` and `.claude/modules/design-studio/workflow.md`, retrieve only the project memory domains declared by the manifest plus directly applicable active rules, then execute the staged specialist workflow.

The primary deliverable is not a prose concept. Maintain a runnable mockup in the project's actual UI stack plus the synchronized current-state design system:
- `.design-studio/mockup/` or the project's established prototype/preview location
- `.docs/design/STYLE_GUIDE.md`
- `.docs/design/tokens.json` or the project's existing token source when appropriate

Detect the project's real framework, styling approach, component conventions, and primary target device before designing. Do not switch to a different stack merely because it is easier to prototype.

Do not load every agent definition into the parent context. Dispatch each specialist only for its phase. Preserve structured disagreement and let the Creative Director resolve conflicts.

For every user-requested design revision, update the mockup and style guide/tokens in the same iteration. Do not create a separate approval or final-decision file when the current synchronized artifacts already express the accepted design.

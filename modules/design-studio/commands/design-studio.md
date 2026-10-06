---
description: Activate the remote design-studio module and create or revise the project's design system
---

Run the installed `design-studio` module workflow. If this command exists, the module has already been installed by the bootstrap module manager. Read `.claude/modules/design-studio/manifest.json` and `.claude/modules/design-studio/workflow.md`, retrieve only the project memory domains declared by the manifest plus any directly applicable active rules, then execute the staged specialist workflow.

Do not load every agent definition into the parent context. Dispatch each specialist only for its phase. Preserve structured disagreement and let the Creative Director resolve conflicts. The final deliverable must be coherent and implementation-ready rather than a bundle of unrelated specialist opinions.

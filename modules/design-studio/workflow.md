# Design Studio Workflow

The module operates as a staged studio, not eight independent generators.

## Phase 1: Brief and context
Creative Director leads. Brand Strategist and Reference Analyst contribute.
- inspect the repository and existing product
- retrieve only design-relevant project rules, learnings, decisions, research, and style guidance
- identify audience, product purpose, constraints, existing brand signals, implementation stack, and explicit user requirements
- write a compact internal design brief and a list of anti-goals

## Phase 2: Experience architecture
UX Architect leads with Brand Strategist and Creative Director.
- information architecture
- navigation and primary flows
- hierarchy and content density
- responsive behavior
- important states and edge cases

## Phase 3: Creative exploration
Art Director, UI Designer, and Motion Designer propose one coherent direction.
- visual language
- typography, color, depth, imagery, iconography
- layout and component language
- interaction and motion grammar
Do not create multiple generic directions unless the user explicitly asks for options.

## Phase 4: Structured critique
Each relevant specialist returns exactly:
1. strongest part
2. weakest part
3. largest risk
4. concrete improvement

The Creative Director resolves disagreements. Distinctiveness, clarity, feasibility, accessibility, and product positioning must all be represented.

## Phase 5: Systemization
Design Systems Engineer leads with UI and Motion.
Produce implementation-ready foundations:
- semantic design tokens
- typography and spacing scales
- color roles and states
- radii, elevation, borders
- component principles and variants
- responsive rules
- motion tokens and reduced-motion behavior
- accessibility constraints
- do / don't guidance

## Phase 6: Final review
Creative Director, UX Architect, and Design Systems Engineer review the complete system for coherence, feasibility, accessibility, and contradictions.

## Output
Write durable project outputs under `.docs/design/`:
- `00-creative-direction.md`
- `01-brand-foundations.md`
- `02-experience-architecture.md`
- `03-visual-system.md`
- `04-component-system.md`
- `05-motion-system.md`
- `06-accessibility-responsive.md`
- `07-do-dont.md`
- `DESIGN_SYSTEM.md` as the concise source of truth used during implementation
- `tokens.json` when concrete tokens can be expressed safely

Store rejected approaches and durable project-specific lessons in the normal decision/learning system rather than bloating `DESIGN_SYSTEM.md`.

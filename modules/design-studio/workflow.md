# Design Studio Workflow

The module operates as a staged studio that produces and maintains a living design implementation, not a bundle of design opinions.

## Core output contract

The design studio always maintains three synchronized outputs:

1. **Runnable mockup source** using the project's actual frontend/application stack.
2. **`.docs/design/STYLE_GUIDE.md`** as the human-readable current design system.
3. **`.docs/design/tokens.json`** as the machine-readable token source when the stack can consume structured tokens.

These are current-state artifacts. They are edited in place throughout the design process. Do not create a new decision file for ordinary user feedback such as changing colors, spacing, corners, layout, typography, motion, or component treatment. The accepted state is simply the latest synchronized mockup, style guide, and tokens.

A separate decision record is warranted only when the rationale itself is durable project knowledge that future agents need independently of the current design state.

## Phase 1: Brief, target, and stack detection
Creative Director leads. Brand Strategist and Reference Analyst contribute.

- inspect the repository and existing product
- retrieve only design-relevant project rules, learnings, decisions, research, and style guidance
- determine the real implementation stack from repository evidence, including framework, styling system, component library, icon system, animation library, and existing design tokens
- determine the product's primary target surface from repository evidence and the user's request: desktop web, responsive web, mobile web, native mobile, tablet, desktop application, or another concrete target
- identify audience, product purpose, constraints, existing brand signals, implementation limitations, and explicit user requirements
- write a compact internal design brief and anti-goals
- do not invent a replacement stack merely because another stack would be easier to mock up

If the project is React + Tailwind, the mockup is React + Tailwind. If it is Next.js, use the project's Next.js conventions. If it is React Native or Expo, produce native mobile screens with that stack. If it is another established UI stack, stay inside it.

When the repository has no UI stack yet, choose the smallest stack consistent with explicit project direction. Treat that as a proposal until the user accepts it.

## Phase 2: Experience architecture
UX Architect leads with Brand Strategist and Creative Director.

- information architecture
- navigation and primary flows
- hierarchy and content density
- responsive behavior
- important states and edge cases
- identify the minimum representative screen set needed to prove the design system

The representative screen set should exercise the actual system rather than produce decorative one-off pages. Include enough screens/states to validate navigation, hierarchy, forms or controls, content surfaces, feedback states, and responsive behavior relevant to the product.

## Phase 3: Creative direction and first mockup
Art Director, UI Designer, and Motion Designer work from the approved brief and UX architecture.

Define one coherent direction:
- visual language
- typography
- semantic color roles
- layout and spacing
- corners, borders, elevation, depth, and surface treatment
- imagery and iconography
- component language
- interaction and motion grammar
- target viewport/device behavior

Then build the first representative mockup in the detected project stack.

### Mockup location

Use `.design-studio/mockup/` as the default isolated working area unless the project already has an established prototype, Storybook, preview, or design-demo location that is clearly better.

The mockup:
- uses the same language, framework, styling approach, and relevant UI dependencies as the project
- may reuse existing project components when doing so does not couple the mockup dangerously to unfinished production behavior
- must not introduce a parallel framework or styling system
- should be runnable or previewable with the project's normal tooling when practical
- is not production code merely because it uses production technology
- should remain isolated enough that iteration cannot accidentally change the shipping application

For a desktop-first product, render desktop-first representative screens. For a mobile-first/native product, render mobile screens at realistic device dimensions. For responsive products, include the primary viewport plus only the additional breakpoint states needed to prove the system.

## Phase 4: Structured critique
Each relevant specialist critiques the actual mockup, not an abstract proposal.

Each specialist returns exactly:
1. strongest part
2. weakest part
3. largest risk
4. concrete improvement

The Creative Director resolves disagreements. Distinctiveness, clarity, feasibility, accessibility, product positioning, and implementation cost must all be represented.

The UI Designer and Design Systems Engineer apply accepted critique directly to the mockup and design-system artifacts before presenting the concept to the user.

## Phase 5: Systemization
Design Systems Engineer leads with UI and Motion.

Derive the design system from what is actually implemented in the mockup. Do not document hypothetical values that the mockup does not use.

Maintain `.docs/design/STYLE_GUIDE.md` with the current authoritative values and rules for at least:

- design principles and visual direction
- color tokens and semantic roles
- typography families, weights, sizes, line heights, and hierarchy
- spacing scale
- page/container margins
- component padding and gaps
- corner/radius scale
- borders, strokes, dividers, and edge treatment
- elevation, shadows, overlays, and depth rules
- surface/background hierarchy
- sizing conventions
- grid/layout/container behavior
- breakpoints and responsive behavior
- component anatomy and major variants
- interactive states
- iconography and imagery rules
- motion durations, easing, transitions, and reduced-motion behavior
- accessibility requirements
- explicit do / don't guidance

Maintain `.docs/design/tokens.json` with machine-readable values wherever useful. Prefer semantic token names over values tied to one component.

Where the project already has a token mechanism, map or generate the mockup from that mechanism instead of creating a competing token system.

## Phase 6: User review loop
The user reviews the runnable mockup or representative screens.

When the user requests a change:
1. treat the feedback as authoritative design input
2. update the mockup implementation
3. update `STYLE_GUIDE.md`
4. update `tokens.json` or the project's existing token source
5. verify the three still agree
6. present the revised concept

Do this for every revision. Never leave the style guide describing the previous version of the mockup. Never leave unused old tokens as accidental historical baggage.

Do not create a separate "final decision" file just because the user approves a revision. Approval means the current synchronized artifacts are already the accepted design.

If feedback contradicts an earlier project rule or an explicit hard constraint, surface the conflict instead of silently rewriting policy.

## Phase 7: Final review
Creative Director, UX Architect, and Design Systems Engineer review the current mockup and synchronized design system.

Check:
- visual coherence
- usability
- implementation feasibility
- accessibility
- responsive/device suitability
- token consistency
- no undocumented magic values where a token should exist
- no documented tokens/rules contradicted by the mockup
- no obsolete design artifacts presented as current state

The final state is ready for production implementation precisely because the representative UI already exists in the project's stack and the current style guide describes that implementation.

## Durable outputs

Required:
- `.design-studio/mockup/` or the project's established equivalent
- `.docs/design/STYLE_GUIDE.md`
- `.docs/design/tokens.json` when structured tokens are appropriate

Optional supporting current-state files may exist under `.docs/design/` only when they improve usability of the system. Avoid splitting one source of truth into many documents without a concrete need.

Rejected explorations are disposable unless their rationale is genuinely useful later. Durable design lessons belong in the normal learning system; durable architectural/design rationale may use the normal decision system. Neither replaces the living style guide.

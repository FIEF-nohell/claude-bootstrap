# Design Studio Craft Standards

This is the design studio's quality floor. It is inspired by public frontend-design guidance from Anthropic, Impeccable, Microsoft frontend review guidance, and other design-agent practices, but is written as project-local policy for this module.

## 1. Start from product specificity

Before choosing colors, type, cards, or motion, identify:

- the product's unique mechanism in one sentence
- the user's real operating scene
- the primary job of the surface
- what would make a polished result still feel wrong
- the category's obvious visual default

Derive the visual system from the product mechanism and user world, not from the category's common SaaS template.

Quality test: if the same surface could be relabeled for an unrelated productivity app with only copy and accent-color changes, the design is not specific enough and must be reworked.

## 2. Classify the surface before designing

Use one of four modes:

- Operate: the user completes a task. Product UI, tools, dashboards, editors, settings.
- Persuade: the user decides and acts. Marketing, pricing, campaigns, landing pages.
- Read: the user understands information. Docs, guides, articles, help.
- Experience: the artifact itself is the experience. Portfolios, galleries, showcases.

For Operate surfaces, scanability, task clarity, repeated-use comfort, state handling, and platform expectations outrank spectacle. Distinctiveness should live in structure, typography, interaction, rhythm, and a small number of memorable details.

## 3. Anti-default reflex check

Do not treat common UI patterns as forbidden. Familiarity is often good product design. The failure is using a pattern automatically without checking whether it serves the product.

Use this list as a reflex check, not a ban list. A familiar card, tab bar, system font, progress visualization, or rounded control is valid when it improves clarity or matches the platform. Reject it only when it is substituting for hierarchy, product thinking, or craft.

The preferred default for product UI is:

**familiar shell + product-specific core interaction + unusually careful execution**

Ask whether the design is relying too heavily on any of these defaults:

- piles of same-size rounded cards used as page structure
- nested cards
- a hero metric with supporting mini-stats
- decorative progress rings as the main visualization
- an eyebrow/kicker above every heading
- purple/blue SaaS gradients
- glass/blur used as decoration
- soft rounded rectangles standing in for hierarchy
- every element receiving the same radius
- emoji or Unicode glyphs used as the icon system
- a generic system font or common AI-default font as the product's only visual voice
- monochrome interfaces with one arbitrary neon accent
- motion consisting of identical fade/slide entrances everywhere
- fake technical styling such as monospace used decoratively

Cards are appropriate when an object genuinely benefits from containment, grouping, elevation, or interaction. They become a problem when every region is independently boxed and hierarchy disappears into a stack of equal-weight containers.

The goal is not visual novelty. A polished, conventional solution is better than a distinctive solution that feels forced, themed, or less usable.

## 3.5 Familiarity and identity

For Operate-mode product UI:

- preserve platform-native expectations for navigation, back behavior, sheets, forms, selection, and controls
- keep the main task immediately understandable without explanation
- concentrate identity in a few durable places: typography, spacing rhythm, data/goal visualization, one core interaction, copy tone, icon treatment, or content imagery
- accent color should usually be selective rather than painted across every control
- avoid visual metaphors that force every surface to imitate a physical object
- metaphors may inspire one interaction or organizing principle, but they must not become a costume
- when in doubt between clever and clear, choose clear, then improve the craft

A design can be specific without being strange. The test is whether its composition, interaction, and detail feel intentional for this product, not whether nobody has ever used the same component before.

## 4. Composition before chrome

Establish hierarchy with:

- grouping
- whitespace
- alignment
- type scale
- contrast
- ordering
- rhythm
- meaningful dividers or surfaces

Only then add containers, shadows, borders, or decorative effects.

Prefer fewer, stronger regions over many interchangeable components.

## 5. Typography is part of identity

Use typography intentionally:

- choose a type voice that matches the product and audience
- preserve strong readability for repeated-use product surfaces
- use obvious hierarchy through size, weight, width, leading, and rhythm
- do not solve hierarchy by adding labels above labels
- keep display tracking restrained
- test real copy, not lorem ipsum
- document the chosen type roles and fallback behavior

## 6. Color must have a job

Define semantic color roles before decorative accents.

- primary text, secondary text, muted text
- canvas, surface, elevated surface
- action, selected, success, warning, error
- separators and focus
- data visualization roles when needed

Secondary text on colored surfaces should be derived from that surface/foreground relationship rather than default gray.

Do not distribute accent colors evenly. One dominant field plus selective accents is usually stronger than a rainbow of equal emphasis.

## 7. Depth and shape must be coherent

Choose a depth system deliberately:

- flat + separators
- border-led
- shadow-led
- material/elevation-led

Do not stack border + wide shadow + glow by reflex.

Use a small radius vocabulary. Large pills belong to controls that are actually pill-like; entire interfaces should not become inflated capsules unless the visual world requires it.

## 7.5 Brand signature

A polished product can still be forgettable. Before finalizing a direction, define one memorable signature system that can recur across the product without compromising clarity.

Choose one primary signature from:
- distinctive typography or wordmark behavior
- mascot or character system
- illustration or photography language
- proprietary icon/shape language
- a recurring spatial/compositional motif
- a product-specific visualization
- a recognizable motion behavior
- a material/surface treatment tied to the brand

Rules:
- the signature must be visible in at least two representative surfaces, not only a splash screen
- it should be recognizable without relying on the logo alone
- it must not require every component to become branded decoration
- it should strengthen the product mechanism or emotional tone
- typography may carry significant identity when the rest of the shell stays restrained
- mascots and illustration are optional, not mandatory; use them when the product benefits from a character or emotional guide
- avoid adding a signature after the fact as ornament. It should influence composition, interaction, or visual rhythm

Quality test: blur the copy and remove the logo. There should still be at least one recurring visual or interaction cue that makes the product feel like itself.

## 8. Product-specific interaction

For repeated-use product UI, identify one or two interactions that express the product mechanism.

Examples:
- a completion action that physically reflects the system's concept
- a weekly planning gesture tied to the product's cadence
- a meaningful transition between overview and detail

Do not scatter decorative micro-interactions. One authored interaction is better than twenty generic ones.

## 9. Shipping-state floor

Representative mockups must show or account for:

- normal
- selected/active
- hover where relevant
- keyboard focus where relevant
- disabled
- loading
- empty
- error/recovery
- completion/success

Use real product language. Controls name their action. Errors name the problem and recovery.

## 10. Accessibility and device reality

Verify the actual target surface:

- text contrast meets WCAG AA where applicable
- touch targets are usable on mobile
- focus is visible on keyboard-capable platforms
- color is not the only state indicator
- content reflows without horizontal scrolling
- reduced-motion behavior exists for authored motion
- platform conventions are preserved unless there is a strong reason to replace them

## 11. Independent critique before approval

Run two perspectives independently before final synthesis:

A. Design critique:
- design specificity
- hierarchy
- cognitive load
- emotional fit
- information architecture
- usability
- product character
- typography, color, composition, motion

B. Implementation/craft review:
- token consistency
- responsive behavior
- accessibility
- state coverage
- hardcoded/magic values
- performance hazards
- mockup/style-guide mismatch

Do not let B's mechanical findings anchor A's aesthetic judgment. Synthesize only after both are complete.

Each critique must name:
- strongest part
- weakest part
- largest risk
- concrete improvement
- specificity verdict: authored for this product or category-interchangeable

A category-interchangeable verdict does not automatically block approval if the interface is intentionally conventional and exceptionally well executed. It blocks approval only when the sameness comes from unexamined defaults rather than a deliberate choice.

A forced-or-costumed verdict also blocks approval. Reviewers must explicitly distinguish:
- generic by accident
- familiar by intent
- specific and appropriate
- forced originality

## 12. Bounded visual QA

When browser/device rendering is available:

1. render all representative target device classes in one inspection batch
2. inspect hierarchy, overflow, spacing rhythm, state coverage, and visual specificity
3. fix all observed issues in one batch
4. perform at most one confirmation pass

Do not enter an open-ended polishing loop.

## 13. Living-system rule

The runnable mockup, STYLE_GUIDE.md, and token source are one design state expressed three ways.

Every accepted revision updates all affected representations in the same iteration. User approval means the synchronized current state is the decision. Do not create redundant approval documents.

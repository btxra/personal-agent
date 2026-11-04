# Interface audit checklist

Adapted from Unslop by Damir Sokolovsky ([@heydamir](https://x.com/heydamir)): [signs](https://github.com/heydamir/unslop/blob/a6f121eee5f29c2f74976b75456feae8b66afb3a/skills/unslop/references/signs.md) and [tokens](https://github.com/heydamir/unslop/blob/a6f121eee5f29c2f74976b75456feae8b66afb3a/skills/unslop/references/tokens.md). [CC BY 4.0](../../../licenses/unslop-CC-BY-4.0.txt). Modified to use the project's design system and accessibility needs instead of fixed aesthetic bans or universal token values.

For each finding, name the element, observable problem, user impact, and smallest plausible correction. A stylistic difference without a usability or consistency problem is an optional suggestion.

- **Hierarchy:** Is the primary task clear? Do competing highlights obscure important content? Does the emphasis fit the product?
- **Spacing:** Do equivalent rows and components align and share spacing? Does grouping reflect relationships? Prefer existing spacing tokens over isolated offsets.
- **Color:** Are semantic colors meaningful and consistent? Measure foreground/background contrast, including interactive states; do not infer compliance from appearance alone.
- **Icons:** Are icons understandable, aligned, and consistently sized? Preserve approved marks and avoid changing an established icon system just to impose a preference.
- **Copy and data:** Are labels specific, claims supportable, numbers consistently formatted, and comparison periods explicit? Keep real content; identify placeholders as examples.
- **Type:** Are the intended hierarchy and reading order clear? Check small text, zoom, long labels, and localization without imposing a universal font or weight.
- **Layout:** Does the screen work at its intended widths without clipped content or accidental horizontal scrolling? Preserve meaningful content order and touch-target accessibility.
- **Details and interaction:** Inspect focus visibility, keyboard navigation, hover/pressed/disabled states, validation, empty states, and loading/error feedback where relevant.
- **Visuals:** Does an illustration explain the product or task? Keep relevant content; propose removal of distracting decoration only when justified by the approved direction.
- **Motion:** Does animation explain a state change? Check reduced-motion behavior and avoid unnecessary repeated movement. Prefer inexpensive transitions where the design permits.

Recheck each changed finding in the rendered result. Do not claim a whole-site accessibility audit from a single-screen review.

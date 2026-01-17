# UI & Visual Implementation Rules

## Visual Fidelity
- **Screenshot Matching:** When provided with a design screenshot, analyze it deeply to match:
  - Spacing and layout (margin, padding, grid/flex alignment).
  - Typography (font size, weight, color).
  - Color palette (extract hex codes if not provided).
- **Visual Bugs:** If a textual description of a UI bug is ambiguous, request a screenshot.

## Accessibility (VAG Compliance)
- **Semantic HTML:** Use proper HTML5 semantic elements (`<nav>`, `<main>`, `<article>`, etc.) instead of generic `div` soup.
- **ARIA Labels:** Ensure interactive elements (buttons, links, inputs) have accessible names (`aria-label`, `aria-labelledby`, or visible text).
- **Keyboard Navigation:** All interactive elements must be focusable and usable via keyboard.
- **Color Contrast:** maintain WCAG AA standard for text contrast.

---
title: Render Interactive Image Hit Regions as Native Controls
date: 2026-07-17
category: ui-bugs
module: microsim-generator
problem_type: ui_bug
component: tooling
symptoms:
  - Keyboard focus skips interactive regions drawn over an image
  - Screen readers do not expose the regions as named controls
  - Enter and Space cannot perform the same action as a pointer click
root_cause: wrong_api
resolution_type: code_fix
severity: high
tags: [accessibility, keyboard, semantic-html, focus-visible, playwright, generated-assets]
---

# Render Interactive Image Hit Regions as Native Controls

## Problem

An image overlay can look interactive while remaining absent from the keyboard
and accessibility tree. The grid infographic runtime positioned generic `div`
elements over image regions and attached pointer and click listeners, so mouse
users could explore content and answer quizzes while keyboard and screen-reader
learners could not reach the same controls.

## Symptoms

- Tab skipped every learning zone and moved directly to later controls.
- The accessibility tree had no named control for any zone.
- Enter and Space could not select a zone in Explore or Quiz mode.
- There was no visible focus treatment corresponding to pointer hover.

## What Didn't Work

- **Treating a click listener as semantics.** A generic element does not become
  a button merely because JavaScript listens for `click`.
- **Relying on the image's printed labels.** Text rendered inside an image does
  not provide a stable programmatic name for the transparent hit region above
  it.
- **Adding only `tabindex` and a keydown handler.** That recreates part of native
  button behavior while leaving role, activation edge cases, and future browser
  behavior as application-owned code.
- **Testing only pointer behavior.** A passing click test cannot prove role,
  name, tab order, keyboard activation, or focus visibility.

## Solution

Use a native button as the hit region and let the data model supply its name:

```javascript
const el = document.createElement('button');
el.type = 'button';
el.className = 'grid-zone';
el.setAttribute('aria-label', zone.label);
el.addEventListener('click', () => this._onZoneClick(zone.id));
```

The shipped runtime applies this contract at
`skills/microsim-generator/assets/infographic-overlay/shared-libs/grid-diagram.js:128-160`.
Because Enter and Space already dispatch a native button click, the existing
Explore and Quiz handler remains the single activation path rather than gaining
a parallel keyboard branch.

Reset the browser's button chrome without removing the semantics, then pair
focus with the existing hover treatment and add a visible inner ring:

```css
.grid-zone {
  appearance: none;
  padding: 0;
  background: transparent;
  border: 2px solid transparent;
}

.grid-zone.zone-hover,
.grid-zone:focus-visible {
  border-color: var(--zone-color);
}

.grid-zone:focus-visible {
  outline: 3px solid white;
  outline-offset: -6px;
  box-shadow: inset 0 0 0 6px var(--zone-color);
}
```

The complete style is at
`skills/microsim-generator/assets/infographic-overlay/shared-libs/grid-overlay.css:76-122`.
The inset ring remains visible when the image wrapper clips overflow and when a
zone touches an image edge.

Focus lifecycle matters after activation as well. The quiz moves focus into its
confirmation dialog, then returns it to the answered zone after the learner
advances (`grid-diagram.js:330-381`). Edit mode is a separate interaction: it
removes learning-zone buttons from sequential focus while preserving the
pointer-based calibration handles (`grid-diagram.js:421-443`).

Finally, protect both behavior and distribution. The static contract requires
native zone construction and byte-identical canonical/public JS and CSS copies
(`skills/microsim-generator/tests/test_infographic_overlay_contract.py:87-99`).
The browser contract verifies accessible roles and names, exact tab order,
Enter and Space, pointer parity, quiz focus return, edit-mode focus exclusion,
and desktop/mobile geometry
(`skills/microsim-generator/tests/test_infographic_overlay_browser.spec.js:55-148`).
The fix is enforced on the default branch after
[PR #34](https://github.com/yaniv256/dmccreary-claude-skills/pull/34).

## Why This Works

Native controls combine four contracts that a pointer hit target otherwise has
to reconstruct separately: semantics, accessible naming, sequential focus, and
keyboard activation. Styling the button preserves the visual overlay while the
browser continues to own those behavioral guarantees.

The browser test checks the learner-facing behavior, while the static parity
test prevents a second failure mode specific to generators: fixing the
canonical asset but continuing to publish a stale runtime copy.

## Prevention

- Treat every clickable region over an image, canvas, or diagram as a real
  control unless it is genuinely decorative.
- Prefer `button` or `a` over `role`, `tabindex`, and hand-written key handlers.
- Source the accessible name from structured data, not pixels in the image.
- Use `:focus-visible` so keyboard focus is obvious without imposing a focus
  ring on every pointer interaction.
- Test the accessibility tree with role-and-name queries, then test Tab order
  and both Enter and Space through a real browser.
- Include pointer activation in the same test so accessibility work cannot
  silently regress existing mouse behavior.
- Exercise focus transfer into and out of dialogs; activation alone is not a
  complete keyboard workflow.
- When a generator has canonical and published asset copies, assert byte
  parity in CI instead of relying on a manual sync step.
- Keep authoring guidance input-neutral: say "select" or "activate," not only
  "click."

## Related Issues

- [Grid overlay accessibility investigation](../../investigations/2026-07-17-grid-overlay-zone-accessibility.md)
- [Keep Behavioral Documentation Synchronized with Executable Contracts](../logic-errors/behavioral-documentation-needs-executable-contracts.md)
- [Remediation PR #34](https://github.com/yaniv256/dmccreary-claude-skills/pull/34)

# Investigation: Grid Overlay Zones Are Mouse-Only

## Summary

The grid infographic runtime generated every learning zone as an absolutely
positioned `div`. It attached pointer-enter, pointer-leave, and click listeners,
but provided no native interactive semantics, accessible name, tab stop,
keyboard activation, or visible focus treatment. Keyboard and screen-reader
learners therefore could not explore a zone or answer a quiz question.

## Reproduction

1. Open `docs/sims/grid-overlay-test/main.html`.
2. Press Tab from the document body.
3. Observe that focus skips all three infographic zones and reaches the mode
   controls instead.
4. Inspect the accessibility tree and observe that no zone is exposed as a
   named control.
5. Enter Quiz mode and observe that Enter and Space cannot submit a zone.

The source defect was present in both the canonical generator runtime and the
byte-identical public copy:

- `skills/microsim-generator/assets/infographic-overlay/shared-libs/grid-diagram.js`
- `docs/sims/shared-libs/grid-diagram.js`

## Root Cause

The first grid runtime implementation modeled a zone as a pointer hit target
rather than an interactive control. Its click handler correctly centralized
Explore and Quiz behavior, but the DOM element feeding that handler was a
generic `div`. Documentation reinforced the assumption by calling zones
"clickable" and recommending a "click-to-explore" prompt.

## Resolution Contract

- Render every normal zone as `<button type="button">`.
- Use the zone label as the button's accessible name.
- Let native button behavior provide Enter and Space activation; do not add a
  parallel keydown implementation.
- Give `:focus-visible` the same highlight as hover plus a high-contrast ring.
- Return focus to the answered zone after the quiz confirmation dialog closes.
- Remove zone buttons from sequential focus in edit mode, where calibration
  handles own the interaction.
- Keep canonical and public JS/CSS copies byte-identical.
- Gate roles, names, tab order, keyboard activation, quiz behavior, focus
  visibility, and responsive layout with static and Playwright tests.

## Scope Boundary

This fix preserves the existing pointer interaction, quiz scoring, and edit
calibration model. It does not redesign the calibration handles as a complete
keyboard geometry editor.

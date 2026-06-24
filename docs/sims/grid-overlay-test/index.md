---
title: Grid Overlay Test — Textbook Intelligence Levels
hide: toc
---

<iframe src="./main.html" width="100%" height="700px" scrolling="no" style="border:none;"></iframe>

[View Fullscreen](./main.html){ .md-button .md-button--primary }

## About This MicroSim

This is a test case for the **grid-overlay** variant of the `interactive-infographic-overlay` skill.
It demonstrates `grid-diagram.js` and `grid-overlay.css` rendering rectangular zones over an SVG infographic.

Click any column in Explore mode to see facts. Switch to Quiz Me to test your knowledge.

## Zones

1. **Static — Level 1** — Fixed PDF or print content with no interactivity
2. **Interactive — Level 2** — MkDocs Material site with embedded MicroSims and quizzes
3. **Adaptive — Level 3+** — AI-personalized content that adapts to each learner

## Technical Notes

- Uses `grid-diagram.js` (zone-based overlay) instead of `diagram.js` (point-marker callout)
- Image is an SVG file (`test-image.svg`) — works identically to PNG/JPG
- Uses `?edit=true` URL parameter to enter edit mode and calibrate zone boundaries
- `showLabels: false` in `data.json` — column titles are already printed in the SVG

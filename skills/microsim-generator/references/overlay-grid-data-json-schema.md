# Grid Overlay data.json Schema Reference

This schema is used with `grid-diagram.js` and `grid-overlay.css` for **grid-type** interactive infographics — posters or comparison charts where rectangular zones are drawn over a background image.

Compare to `data-json-schema.md`, which documents the point-marker callout type used with `diagram.js`.

## Complete Schema

```json
{
  "title": "Poster Title",
  "image": "poster-filename.png",
  "layout": "grid",
  "showLabels": false,
  "palette": ["#hex1", "#hex2"],
  "zones": [
    {
      "id": "zone-id",
      "label": "Zone Label",
      "color": "#1389A6",
      "x1": 2.5,
      "y1": 10.0,
      "x2": 35.0,
      "y2": 90.0,
      "summary": "One-line summary shown in the detail panel.",
      "facts": [
        "Bullet fact 1",
        "Bullet fact 2"
      ]
    }
  ],
  "quiz": [
    {
      "question": "Which zone shows ...?",
      "correct_zone": "zone-id",
      "explanation": "Explanation shown after answering."
    }
  ]
}
```

## Top-Level Fields

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `title` | string | Yes | — | Poster title used as image `alt` text |
| `image` | string | Yes | — | Filename of the background infographic image |
| `layout` | string | Yes | — | Must be `"grid"` to signal grid-diagram.js |
| `showLabels` | boolean | No | `false` | Show a color chip label inside each zone. Set `true` only when the image has **no** built-in column/section titles; set `false` (or omit) when titles are printed in the infographic (the chip would overlap them) |
| `palette` | array | No | built-in | Array of hex colors for the quiz confetti celebration |

## Zone Fields

Each object in the `zones` array defines one clickable rectangular region.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | Yes | Unique kebab-case identifier (e.g., `"digital-signal"`) |
| `label` | string | Yes | Display name shown in the detail panel and as the zone chip when `showLabels` is true |
| `color` | string | Yes | Hex color for the zone border, hover highlight, and chip background |
| `x1` | number | Yes | Left edge of zone as % of image width (0 = left edge) |
| `y1` | number | Yes | Top edge of zone as % of image height (0 = top edge) |
| `x2` | number | Yes | Right edge of zone as % of image width (100 = right edge) |
| `y2` | number | Yes | Bottom edge of zone as % of image height (100 = bottom edge) |
| `summary` | string | Yes | One-line italic summary shown below the zone label in the detail panel |
| `facts` | array | Yes | Bullet-point facts shown as a `<ul>` in the detail panel |

## Quiz Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `question` | string | Yes | Question text displayed above the infographic |
| `correct_zone` | string | Yes | `id` of the zone that is the correct answer |
| `explanation` | string | No | Explanation shown after answering (currently reserved; not yet rendered by grid-diagram.js) |

## Positioning Guidelines

- `x1`, `y1` define the **top-left** corner; `x2`, `y2` define the **bottom-right** corner
- All values are percentages of the image dimensions (0–100)
- Use `?edit=true` appended to the URL to enter edit mode: drag corner handles to calibrate positions visually, then click "Copy JSON" to get updated coordinates
- For comparison-column posters, zones typically run the full height of the content area (e.g., `y1: 10, y2: 90`) and divide the width evenly

## Color Palette Suggestions

| Hex | Color |
|-----|-------|
| `#C7164E` | Crimson |
| `#1389A6` | Teal |
| `#6A3FB5` | Violet |
| `#2D8A4E` | Forest green |
| `#E07B39` | Orange |
| `#2A2E3A` | Dark navy |
| `#E5398A` | Pink |

## Choosing Between Grid and Callout Types

| Scenario | Use |
|----------|-----|
| Comparison infographic with columns or large labeled regions | `grid` (this schema) |
| Scientific illustration with point markers on specific structures | `callout` (`data-json-schema.md`) |
| The image has regions that span large rectangular areas | `grid` |
| Markers need leader lines drawn to small anatomical structures | `callout` |

## Example: 3-Column Comparison Poster

```json
{
  "title": "Static vs. Interactive vs. Adaptive Textbooks",
  "image": "textbook-levels.png",
  "layout": "grid",
  "showLabels": false,
  "palette": ["#1389A6", "#2D8A4E", "#6A3FB5"],
  "zones": [
    {
      "id": "static",
      "label": "Static (Level 1)",
      "color": "#1389A6",
      "x1": 2.0,  "y1": 12.0,
      "x2": 33.0, "y2": 88.0,
      "summary": "Fixed PDF or print content — no interactivity",
      "facts": [
        "Text and static images only",
        "No learner interaction",
        "Same content for every reader",
        "Typically PDF or printed pages"
      ]
    },
    {
      "id": "interactive",
      "label": "Interactive (Level 2)",
      "color": "#2D8A4E",
      "x1": 35.0, "y1": 12.0,
      "x2": 66.0, "y2": 88.0,
      "summary": "Hyperlinked MkDocs site with embedded MicroSims",
      "facts": [
        "Hyperlinked navigation",
        "Interactive simulations (MicroSims)",
        "Embedded quizzes",
        "MkDocs Material theme"
      ]
    },
    {
      "id": "adaptive",
      "label": "Adaptive (Level 3+)",
      "color": "#6A3FB5",
      "x1": 68.0, "y1": 12.0,
      "x2": 98.0, "y2": 88.0,
      "summary": "AI-personalized content that adapts to each learner",
      "facts": [
        "Tracks learner progress (xAPI)",
        "AI-generated explanations on demand",
        "Adapts difficulty and pacing",
        "Knowledge graph drives concept ordering"
      ]
    }
  ],
  "quiz": [
    {
      "question": "Which textbook level uses xAPI to track learner progress and adapts content based on performance?",
      "correct_zone": "adaptive",
      "explanation": "Level 3+ adaptive textbooks use xAPI (Experience API) to log learner interactions and adjust content difficulty or pacing accordingly."
    },
    {
      "question": "Which textbook level uses an MkDocs Material site with embedded MicroSims for student interaction?",
      "correct_zone": "interactive",
      "explanation": "Level 2 interactive textbooks are built with MkDocs Material and embed p5.js/Chart.js MicroSims for hands-on learning without server-side AI."
    }
  ]
}
```

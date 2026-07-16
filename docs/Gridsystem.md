# Grid and placement layout

The backend stores layout hints for items in the children_arrangement and self_alignment fields. These values are saved as text in the database, so the application can interpret them as structured JSON when rendering maps or editors.

## Supported layout modes

### Cloud layout

Use cloud layout when children can be positioned freely rather than in a strict row/column pattern.

Example parent value:

```json
{
  "type": "cloud"
}
```

Example child value:

```json
{
  "type": "cloud_child",
  "relative_points": [[0.5, 0.5], [0.6, 0.7], [0.4, 0.3]]
}
```

### Grid layout

Use grid layout when children should be placed according to a regular row/column pattern.

Example parent value:

```json
{
  "type": "grid",
  "rows": 6,
  "columns": 3,
  "top_left_corner": [0.1, 0.23],
  "bottom_right_corner": [0.9, 0.77]
}
```

Example child value:

```json
{
  "type": "grid_child",
  "row": 2,
  "column": 1
}
```

## Notes

- The backend does not enforce a strict schema for these values.
- The intended format is JSON, but the application treats these fields as free-form text until another layer parses them.
- See PlacementCode.md for how items are organized in the hierarchy.

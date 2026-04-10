### System 🪵

Each element has a "align-children" property that can be set to one of the following values:

- **Cloud** - The children can be anywhere on the map, using draw points to define their position.
- **Grid** - The children are aligned in a grid pattern.

### Storage examples 📦

Example `grid` parent:

```json
(Other properties ...)
children-arrangement: {
    "type": "grid",
    "rows": 6,
    "columns": 3,
    "top_left_corner": [0.1, 0.23],
    "bottom_right_corner": [0.9, 0.77]
}
```

Example `grid` child:

```json
(Other properties ...)
self-alignment: {
    "type": "grid_child",
    "row": 2,
    "column": 1
}
```

Example `cloud` parent:

```json
(Other properties ...)
children-arrangement: {
    "type": "cloud"
}
```

Example `cloud` child:

```json
(Other properties ...)
self-alignment: {
    "type": "cloud_child",
    "relative_points": [[0.5, 0.5], [0.6, 0.7], [0.4, 0.3]]
}
```

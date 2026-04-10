# Database Layout

## Inholders

| Value              | Description                               | Data type / format                                                                                           |
| ------------------ | ----------------------------------------- | ------------------------------------------------------------------------------------------------------------ |
| placement_code     | a list of location_codes                  | TEXT NOT NULL, list of the placement_codes of the parents, separated by `-`. Must be A-Z (upper case) or 0-9 |
| name               |                                           | TEXT NOT NULL                                                                                                |
| description        | format: markdown                          | TEXT                                                                                                         |
| keywords           |                                           | TEXT, list of keywords separated by `,`                                                                      |
| self_alignment     | Described in [Gridsystem](Gridsystem.md). | TEXT                                                                                                         |
| children_arrangeme | Described in [Gridsystem](Gridsystem.md). | TEXT                                                                                                         |
| color              | The color of the inholder                 | TEXT, Hexadecimal code                                                                                       |

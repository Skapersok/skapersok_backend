# Placement code

Placement codes define the hierarchy of items in the database. Each item has a unique placement code, and no two items may share the same code.

## Structure

A placement code is built from one or more segments separated by hyphens. Each segment is a label for one level in the hierarchy.

Examples:

- `A`
- `A-1`
- `B-STORAGE`
- `A-1-1`

The empty string `""` is reserved for the root item.

## Rules

A placement code may only contain:

- uppercase letters `A-Z`
- digits `0-9`
- hyphens `-`

The following are not valid:

- lowercase letters
- spaces
- underscores
- slashes
- punctuation marks

## Notes

- Parent-child relationships are derived from the placement code structure.
- The backend validates placement codes before creating or updating items.
- Changing an item's placement code also updates all descendants so the hierarchy remains consistent.

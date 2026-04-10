# Database API Reference

This document provides a comprehensive reference for the ShelfSearch2 database API endpoints and core functions.

## Overview

ShelfSearch is a hierarchical storage management system with a Flask-based REST API. The system features:

- **Hierarchical Storage:** Inholders (items) organized in a tree structure using placement codes
- **Search Capability:** Fuzzy search across all inholders
- **Image Support:** Store maps and descriptions images with automatic format conversion
- **Authentication:** JWT-based authentication with role-based access control
- **Automatic Backups:** Scheduled database backups to ZIP archives
- **Multi-user:** User management with granular permissions

## Table of Contents

- [REST API Endpoints](#rest-api-endpoints)
  - [Authentication](#authentication)
  - [Server Information](#server-information)
  - [Inholder Operations](#inholder-operations)
  - [Search & Navigation](#search--navigation)
  - [Image Operations](#image-operations)
- [Database Functions](#database-functions)
- [Search Module](#search-module)
- [Configuration Module](#configuration-module)
- [Backup Module](#backup-module)
- [Error Responses](#error-responses)
- [Best Practices & Implementation Guide](#best-practices--implementation-guide)
- [Environment Variables](#environment-variables)
- [Data Models](#data-models)

---

## REST API Endpoints

Base URL: `http://localhost:5000` (configurable via `PORT` environment variable)

### Authentication

The API uses JWT (JSON Web Tokens) for stateless authentication. Tokens must be included in the `Authorization` header with the format: `Authorization: Bearer <token>`

**Token Details:**
- **Access Token:** Short-lived token (15 minutes) used to authenticate regular API requests
- **Refresh Token:** Long-lived token (24 hours) used to obtain new access tokens without re-authenticating
- **Storage:** Refresh tokens are stored server-side for revocation support (logout)

#### POST `/login`
Authenticate a user and receive access/refresh tokens.

**Request Body:**
```json
{
  "username": "string",
  "password": "string"
}
```

**Response:**
```json
{
  "access_token": "string (JWT token valid for 15 minutes)",
  "refresh_token": "string (JWT token valid for 24 hours)"
}
```

**Status Codes:**
- `200` - Success
- `400` - Missing or invalid request data (missing username/password)
- `401` - Invalid credentials (user doesn't exist or password incorrect)

**Usage Example:**
```python
import requests

response = requests.post('http://localhost:5000/login', json={
    'username': 'john_doe',
    'password': 'secure_password'
})

tokens = response.json()
access_token = tokens['access_token']
refresh_token = tokens['refresh_token']

# Use access token for subsequent requests
headers = {'Authorization': f'Bearer {access_token}'}
```

---

#### POST `/refresh`
Refresh an expired access token using a valid refresh token.

**Headers:**
- `Authorization: Bearer <refresh_token>`

**Response:**
```json
{
  "access_token": "string (new JWT token)",
  "refresh_token": "string (new JWT token)"
}
```

**Status Codes:**
- `200` - Success
- `401` - Invalid, expired, or missing refresh token

**Behavior:**
- Both access and refresh tokens are refreshed
- Previous refresh token becomes invalid
- Prevents token reuse attacks

---

#### GET `/authorized`
Verify if the current access token is valid.

**Headers:**
- `Authorization: Bearer <access_token>`

**Response:**
```json
{
  "status": "ok"
}
```

**Status Codes:**
- `200` - Token is valid
- `401` - Token is invalid, missing, or expired

**Use Case:** Client can use this endpoint to validate token before making requests or to refresh before token expires.

---

#### POST `/logout`
Invalidate the current refresh token (logout).

**Headers:**
- `Authorization: Bearer <refresh_token>`

**Response:**
```json
{
  "msg": "Logged out"
}
```

**Status Codes:**
- `200` - Success
- `401` - Invalid or missing refresh token

**Behavior:**
- Removes the refresh token from server storage
- The refresh token cannot be used again to obtain new access tokens
- Any access tokens already issued remain valid until expiration

---

### Server Information

#### GET `/server_id`
Get the unique identifier for this server instance.

**Response:**
```json
{
  "id": "string (UUID format)"
}
```

**Status Codes:**
- `200` - Success

**Use Case:** Clients can use this to identify which server they're connected to, useful for discovery and multi-server deployments.

---

#### GET `/ping`
Health check endpoint to verify the server is running and responsive.

**Response:**
```json
{
  "status": "ok"
}
```

**Status Codes:**
- `200` - Server is healthy and responding

**Use Case:** Monitor server availability, connection validation, or keep-alive heartbeat.

---

### Inholder Operations

Inholders are items in the hierarchical storage system. Each inholder has a unique placement code that defines its position in the tree.

**Placement Code Format:**
- Root (top-level): Empty string `""`
- Level 1: `"A"`, `"B"`, `"SECTION"`
- Level 2: `"A-1"`, `"A-2"`, `"B-STORAGE"`
- Level 3+: Continued pattern with hyphens

**Restrictions:**
- Must contain only uppercase alphanumeric ASCII characters and hyphens
- Cannot contain spaces or special characters

#### GET `/get/<placement_code>`
Get a single inholder by placement code.

**Parameters:**
- `placement_code` (path) - The placement code (optional, defaults to root `""`)

**Response:**
```json
{
  "placement_code": "string",
  "name": "string",
  "description": "string",
  "keywords": "string",
  "children_arrangement": "string",
  "self_alignment": "string",
  "color": "string",
  "has_map_image": boolean,
  "has_description_image": boolean
}
```

**Status Codes:**
- `200` - Success
- `404` - Inholder not found

**Examples:**
```bash
# Get root
curl http://localhost:5000/get/

# Get item "A-1"
curl http://localhost:5000/get/A-1
```

---

#### GET `/get_root`
Get the root inholder (placement code `""`).

**Response:**
```json
{
  "placement_code": "",
  "name": "string",
  "description": "string",
  "keywords": "string",
  "children_arrangement": "string",
  "self_alignment": "string",
  "color": "string",
  "has_map_image": boolean,
  "has_description_image": boolean
}
```

**Status Codes:**
- `200` - Success

**Use Case:** Shorthand for `/get/` - some clients may find this more semantic.

---

#### GET `/get_all`
Get all inholders in the database (excludes root).

**Query Parameters:**
- `only_leaves` (optional, string) - If `"true"`, only return leaf nodes (items with no children). Default: `"false"`

**Response:**
```json
[
  {
    "placement_code": "string",
    "name": "string",
    "description": "string",
    "keywords": "string",
    "children_arrangement": "string",
    "self_alignment": "string",
    "color": "string",
    "has_map_image": boolean,
    "has_description_image": boolean
  },
  ...
]
```

**Status Codes:**
- `200` - Success (always succeeds, returns empty array if no items)

**Examples:**
```bash
# Get all inholders
curl http://localhost:5000/get_all

# Get only leaf nodes (storage items with no children)
curl "http://localhost:5000/get_all?only_leaves=true"
```

---

#### GET `/get_children/<placement_code>`
Get direct children of an inholder (immediate descendants only).

**Parameters:**
- `placement_code` (path) - The parent placement code (optional, defaults to root `""`)

**Response:**
```json
[
  {
    "placement_code": "string",
    "name": "string",
    ...
  }
]
```

**Status Codes:**
- `200` - Success (empty array if no children)
- `404` - Parent inholder not found

**Notes:**
- Only returns direct children, not all descendants
- Results are ordered by placement code
- Use with `/get_all` then filter for recursive tree traversal

**Examples:**
```bash
# Get children of root
curl http://localhost:5000/get_children/

# Get children of "A-1"
curl http://localhost:5000/get_children/A-1
```

---

#### GET `/exists/<placement_code>`
Check if an inholder exists in the database.

**Parameters:**
- `placement_code` (path) - The placement code to check (optional, defaults to root `""`)

**Response:**
```json
{
  "exists": boolean
}
```

**Status Codes:**
- `200` - Success (always succeeds, returns false if not found)

---

#### POST `/add`
Add a new inholder to the database.

**Required Permission:** `"add"`

**Content-Type:** 
- `application/json` (for data-only requests)
- `multipart/form-data` (when including image files)

**Request Body/Form Data:**
```json
{
  "placement_code": "string (required, must be unique and valid format)",
  "name": "string (required, display name)",
  "description": "string (optional)",
  "keywords": "string (optional, comma-separated for search)",
  "children_arrangement": "string (optional)",
  "self_alignment": "string (optional)",
  "color": "string (optional, hex color code recommended)"
}
```

**Optional Files:**
- `mapimage` - Map/layout image file (PNG, JPEG, HEIC, etc.)
- `descimage` - Description/detail image file (PNG, JPEG, HEIC, etc.)

**Response:**
```json
{
  "status": "ok"
}
```

**Status Codes:**
- `200` - Success
- `400` - Missing required fields or invalid placement code syntax
- `401` - Unauthorized (no token, invalid token, or lacks "add" permission)
- `409` - Inholder already exists at this placement code

**Placement Code Validation Rules:**
- Must contain only uppercase ASCII alphanumeric and hyphens
- Must not already exist in database
- Parent inholder must exist (e.g., "A-1-B" requires "A-1" and "A" to exist)

**Example:**
```bash
curl -X POST http://localhost:5000/add \
  -H "Authorization: Bearer <access_token>" \
  -F "placement_code=A-1" \
  -F "name=Section A, Shelf 1" \
  -F "description=Main storage section" \
  -F "keywords=storage,shelf,location" \
  -F "mapimage=@map.jpg"
```

---

#### DELETE `/remove/<placement_code>`
Remove an inholder and all its descendants from the database.

**Required Permission:** `"remove"`

**Parameters:**
- `placement_code` (path) - The placement code to remove

**Response:**
```json
{
  "status": "ok"
}
```

**Status Codes:**
- `200` - Success
- `401` - Unauthorized (no token, invalid token, or lacks "remove" permission)
- `404` - Inholder not found

**Behavior:**
- Deletes the specified inholder
- Recursively deletes all children and descendants
- Associated images are also deleted
- Cannot delete the root (placement code `""`)

**Example:**
```bash
curl -X DELETE http://localhost:5000/remove/A-1 \
  -H "Authorization: Bearer <access_token>"
```

---

#### PUT `/update`
Update an existing inholder's properties.

**Required Permission:** `"update"`

**Content-Type:**
- `application/json` (for data-only requests)
- `multipart/form-data` (when including image files)

**Request Body/Form Data:**
```json
{
  "placement_code": "string (required, the item to update)",
  "new_placement_code": "string (optional, to rename the item)",
  "name": "string (optional)",
  "description": "string (optional)",
  "keywords": "string (optional)",
  "children_arrangement": "string (optional)",
  "self_alignment": "string (optional)",
  "color": "string (optional)"
}
```

**Optional Files:**
- `mapimage` - New map image (replaces existing)
- `descimage` - New description image (replaces existing)

**Response:**
```json
{
  "status": "ok"
}
```

**Status Codes:**
- `200` - Success
- `400` - Invalid data or invalid new placement code syntax
- `401` - Unauthorized (no token, invalid token, or lacks "update" permission)
- `404` - Inholder to update not found
- `409` - New placement code already exists

**Behavior:**
- Only provided fields are updated; omitted fields remain unchanged
- `new_placement_code` renames the inholder and updates all descendants' codes
- Image updates replace existing images

**Example:**
```bash
curl -X PUT http://localhost:5000/update \
  -H "Authorization: Bearer <access_token>" \
  -d '{"placement_code":"A-1", "name":"Updated Name", "color":"#FF0000"}'
```

---

#### PUT `/update_root`
Update the root inholder (placement code `""`).

**Note:** Does NOT require authentication permission check (root is always updatable).

**Content-Type:**
- `application/json`
- `multipart/form-data` (when including images)

**Request Body/Form Data:**
```json
{
  "name": "string (optional)",
  "description": "string (optional)",
  "keywords": "string (optional)",
  "children_arrangement": "string (optional)",
  "self_alignment": "string (optional)",
  "color": "string (optional)"
}
```

**Optional Files:**
- `mapimage` - New map image
- `descimage` - New description image

**Response:**
```json
{
  "status": "ok"
}
```

**Status Codes:**
- `200` - Success

**Behavior:**
- Updates the root inholder properties
- Updating the `name` also updates the server display name in beacon broadcasts
- Cannot change the placement code (always empty string)

---

### Search & Navigation

#### GET `/search`
Search for inholders by query string using fuzzy matching.

**Query Parameters:**
- `q` (required, string) - Search query. Empty string returns all items.
- `max_results` (optional, integer) - Maximum number of results to return
- `skip_number` (optional, integer) - Number of results to skip for pagination (default: 0)
- `only_leaves` (optional, string) - If `"true"`, only return leaf nodes. Default: `"false"`

**Response:**
```json
[
  {
    "placement_code": "string",
    "name": "string",
    "description": "string",
    "keywords": "string",
    "children_arrangement": "string",
    "self_alignment": "string",
    "color": "string",
    "has_map_image": boolean,
    "has_description_image": boolean
  },
  ...
]
```

**Status Codes:**
- `200` - Success (returns empty array if no matches)
- `400` - Missing query parameter

**Search Algorithm:**
- Fuzzy matching with 60% default similarity threshold
- Searches both name and keywords fields
- Results ordered by relevance (name matches score higher)
- Empty query returns all items

**Examples:**
```bash
# Search for "shelf"
curl "http://localhost:5000/search?q=shelf"

# Search with pagination
curl "http://localhost:5000/search?q=storage&max_results=10&skip_number=0"

# Search only leaf nodes (storage items)
curl "http://localhost:5000/search?q=shelf&only_leaves=true"

# Get all items (empty query)
curl "http://localhost:5000/search?q="
```

---

#### GET `/trail`
Get the hierarchical trail from root to a specific inholder, including siblings at each level.

**Query Parameters:**
- `c` (required, string) - The placement code to get the trail for

**Response:**
```json
[
  {
    "placement_code": "string",
    "name": "string",
    "description": "string",
    ...,
    "siblings": [
      {
        "placement_code": "string",
        "name": "string",
        ...
      },
      ...
    ]
  },
  ...
]
```

**Status Codes:**
- `200` - Success
- `400` - Missing placement code parameter
- `404` - Inholder not found

**Behavior:**
- Returns path from root to target inholder
- Each level includes the current item and its siblings
- Useful for breadcrumb navigation
- Can be used to render hierarchical menus

**Example Response for `/trail?c=A-1-B`:**
```json
[
  {
    "placement_code": "A",
    "name": "Section A",
    "siblings": [
      {"placement_code": "A", "name": "Section A"},
      {"placement_code": "B", "name": "Section B"}
    ]
  },
  {
    "placement_code": "A-1",
    "name": "Shelf 1",
    "siblings": [
      {"placement_code": "A-1", "name": "Shelf 1"},
      {"placement_code": "A-2", "name": "Shelf 2"}
    ]
  },
  {
    "placement_code": "A-1-B",
    "name": "Box B",
    "siblings": [
      {"placement_code": "A-1-A", "name": "Box A"},
      {"placement_code": "A-1-B", "name": "Box B"}
    ]
  }
]
```

---

#### GET `/has_children/<placement_code>`
Check if an inholder has children (is not a leaf node).

**Parameters:**
- `placement_code` (path) - The placement code to check (optional, defaults to root `""`)

**Response:**
The server returns a JSON array containing a single boolean value:

```json
[true]
```

Where `true` means the inholder has children, `false` means it's a leaf node.

**Status Codes:**
- `200` - Success

**Note:** The response format (array containing boolean) is unusual but reflects the current server implementation.

---

---

### Image Operations

Images are automatically converted to WebP format for efficient storage and transmission. Supported input formats include PNG, JPEG, HEIC, and other formats supported by Pillow.

#### GET `/descimage/<placement_code>`
Get the description image for an inholder.

**Parameters:**
- `placement_code` (path) - The placement code (optional, defaults to root `""`)

**Response:**
- Binary image data (WebP format)

**Status Codes:**
- `200` - Success
- `404` - Inholder or image not found

---

#### GET `/mapimage/<placement_code>`
Get the map image for an inholder.

**Parameters:**
- `placement_code` (path) - The placement code (optional, defaults to root `""`)

**Response:**
- Binary image data (WebP format)

**Status Codes:**
- `200` - Success
- `404` - Inholder or image not found

**Image Format Notes:**
- All images are stored and served in WebP format for efficiency
- Supported upload formats: PNG, JPEG, HEIC, and most Pillow-supported formats
- Images are automatically converted to RGBA before WebP encoding
- Quality setting can be configured via `IMAGE_QUALITY` config variable (default: 85)

---

## Database Functions

These are internal Python functions in the `database.py` module.

### Core Operations

#### `add(placement_code, name, description, keywords, children_arrangement, self_alignment, color)`
Add a new inholder to the database.

**Parameters:**
- `placement_code` (str) - Unique identifier
- `name` (str) - Display name
- `description` (str) - Description text
- `keywords` (str) - Search keywords
- `children_arrangement` (str) - Layout arrangement for children
- `self_alignment` (str) - Self-alignment setting
- `color` (str) - Color value

**Raises:**
- `ValueError` - If placement code syntax is invalid

---

#### `remove(placement_code)`
Remove an inholder and all its descendants.

**Parameters:**
- `placement_code` (str) - The placement code to remove

---

#### `update(placement_code, name, description, keywords, children_arrangement, self_alignment, color)`
Update an existing inholder. Use `None` for any field to skip updating it.

**Parameters:**
- `placement_code` (str) - The placement code to update
- `name` (str | None) - New name (or None to skip)
- `description` (str | None) - New description (or None to skip)
- `keywords` (str | None) - New keywords (or None to skip)
- `children_arrangement` (str | None) - New arrangement (or None to skip)
- `self_alignment` (str | None) - New alignment (or None to skip)
- `color` (str | None) - New color (or None to skip)

---

#### `update_placement_code(old_placement_code, new_placement_code)`
Rename a placement code and update all descendants.

**Parameters:**
- `old_placement_code` (str) - Current placement code
- `new_placement_code` (str) - New placement code

---

### Query Operations

#### `exists(placement_code) -> bool`
Check if an inholder exists.

**Returns:** `True` if exists, `False` otherwise

---

#### `get(placement_code) -> dict | None`
Get full inholder data.

**Returns:** Dictionary with inholder data or `None` if not found

---

#### `get_root() -> dict`
Get the root inholder (placement code `""`).

**Returns:** Dictionary with root inholder data

---

#### `get_all() -> list[dict]`
Get all inholders except the root.

**Returns:** List of inholder dictionaries

---

#### `get_children(placement_code) -> list[str]`
Get direct children placement codes.

**Parameters:**
- `placement_code` (str) - The parent placement code (empty string for root)

**Returns:** List of direct child placement code strings

---

#### `get_siblings(placement_code) -> list[dict]`
Get sibling inholders at the same hierarchical level.

**Parameters:**
- `placement_code` (str) - The placement code

**Returns:** List of inholder dictionaries at the same depth, excluding the node itself

---

#### `is_leaf(placement_code) -> bool`
Check if an inholder has no children.

**Parameters:**
- `placement_code` (str) - The placement code

**Returns:** `True` if leaf node (no children), `False` otherwise

---

#### `search(query, only_leaves, max_results, skip_number=0) -> list[dict]`
Perform fuzzy search on inholders.

**Parameters:**
- `query` (str) - Search query
- `only_leaves` (bool) - If `True`, only return leaf nodes
- `max_results` (int | None) - Maximum results (None for unlimited)
- `skip_number` (int) - Results to skip for pagination

**Returns:** List of matching inholder dictionaries

---

### Image Operations

#### `verify_placement_code_syntax(placement_code) -> bool`
Validate placement code format.

**Rules:**
- Empty string is valid
- Parts separated by `-`
- Each part must be alphanumeric uppercase ASCII or digits only

**Returns:** `True` if valid, `False` otherwise

---

#### `map_image_path(placement_code) -> Path`
Get the file path for a map image.

**Returns:** Path object

---

#### `description_image_path(placement_code) -> Path`
Get the file path for a description image.

**Returns:** Path object

---

#### `set_map_image(placement_code, file)`
Save a map image for an inholder.

**Parameters:**
- `placement_code` (str) - The placement code
- `file` (werkzeug.datastructures.FileStorage) - Uploaded file object

**Supported input formats:** PNG, JPEG, HEIC, and most formats supported by Pillow

**Behavior:**
- Automatically converts uploaded image to WebP format
- Converts image to RGBA color space
- Replaces any existing image
- Stores in `data/img/mapimgs/` directory

**Raises:**
- `ValueError` - If image format is unsupported or file is corrupted

---

#### `set_description_image(placement_code, file)`
Save a description image for an inholder.

**Parameters:**
- `placement_code` (str) - The placement code
- `file` (werkzeug.datastructures.FileStorage) - Uploaded file object

**Supported input formats:** PNG, JPEG, HEIC, and most formats supported by Pillow

**Behavior:**
- Automatically converts uploaded image to WebP format
- Converts image to RGBA color space
- Replaces any existing image
- Stores in `data/img/descimgs/` directory

**Raises:**
- `ValueError` - If image format is unsupported or file is corrupted

---

#### `has_map_image(placement_code) -> bool`
Check if a map image exists.

**Returns:** `True` if image exists, `False` otherwise

---

#### `has_description_image(placement_code) -> bool`
Check if a description image exists.

**Returns:** `True` if image exists, `False` otherwise

---

### User Management

#### `create_user(username, password, permissions)`
Create a new user account.

**Parameters:**
- `username` (str) - Username
- `password` (str) - Password (will be hashed)
- `permissions` (list[str]) - List of permission strings

**Available Permissions:**
- `"add"` - Can add inholders
- `"update"` - Can update inholders
- `"remove"` - Can remove inholders
- `"rename_server"` - Can rename the server

---

#### `get_user_by_username(username) -> dict | None`
Get user data by username.

**Returns:** User dictionary or `None` if not found

---

#### `verify_user(username, password) -> dict | None`
Verify user credentials.

**Returns:** User dictionary if valid, `None` otherwise

---

#### `set_permissions(username, permissions)`
Update user permissions.

**Parameters:**
- `username` (str) - Username
- `permissions` (list[str]) - New permission list

---

#### `list_users() -> list[dict]`
Get all users.

**Returns:** List of user dictionaries (without password hashes)

---

#### `user_exists(username) -> bool`
Check if a username exists.

**Returns:** `True` if exists, `False` otherwise

---

#### `user_by_id(id) -> dict | None`
Get user by ID.

**Returns:** User dictionary or `None` if not found

---

## Search Module

Located in `search.py`, provides fuzzy search functionality using weighted scoring on inholder names and keywords.

#### `get_search_data() -> list[dict]`
Get the current search index data.

**Returns:** List of dictionaries with the following structure:
```python
{
  "placement_code": str,  # Placement code of the inholder
  "text": str             # Combined searchable text (name + keywords)
}
```

---

#### `fuzzy_search(query, limit, cutoff=60) -> list[str]`
Perform fuzzy search on inholders using the search index.

**Parameters:**
- `query` (str) - Search query string
- `limit` (int | None) - Maximum number of results to return (None for unlimited)
- `cutoff` (int) - Minimum similarity score (0-100, default 60)

**Returns:** List of matching placement code strings, ordered by relevance

**Notes:**
- Uses weighted fuzzy matching where name matches score higher than keyword matches
- Empty query returns all items in database order
- Results are cached and indexed in memory for performance

---

## Configuration Module

Located in `config.py`, manages persistent configuration stored in `.env` file. The module provides a simple key-value interface for storing and retrieving configuration values.

#### `get(key, default=None) -> str | bool | None`
Get a configuration value.

**Parameters:**
- `key` (str) - Configuration key name
- `default` (str | bool | None) - Default value to return if key doesn't exist. If provided, this value is also written to the `.env` file.

**Returns:** Configuration value as string or boolean, or the default value if not found

**Behavior:**
- If key exists, returns the stored value
- If key doesn't exist and default is `None`, returns `None`
- If key doesn't exist and default is provided, writes the default to `.env` and returns it

---

#### `set(key, value=True)`
Set or update a configuration value in the `.env` file.

**Parameters:**
- `key` (str) - Configuration key name
- `value` (str | bool) - Value to set (default: `True`)

**Behavior:**
- Creates or updates the key in `.env`
- Changes are written immediately to disk

---

#### `delete(key)`
Remove a configuration key from the `.env` file.

**Parameters:**
- `key` (str) - Configuration key name to remove

---

#### `isset(key) -> bool`
Check if a configuration key exists.

**Parameters:**
- `key` (str) - Configuration key name

**Returns:** `True` if key exists in `.env`, `False` otherwise

---

## Backup Module

Located in `backups.py`, handles automated and manual database backups. Backups are created as ZIP archives containing the complete database data folder.

#### `create_backup()`
Create a single backup of the entire database data folder.

**Behavior:**
- Creates a ZIP file in the configured `BACKUP_FOLDER`
- Backup files are named with the format: `YYYY-MM-DD.zip` (with numeric suffix if multiple backups on same day)
- Backs up the complete `data/` directory with all inholders and images

**Returns:** None

**Raises:**
- May raise file system errors if backup directory is inaccessible

---

#### `periodic_backup(sleep_time)`
Run continuous backup loop (designed for background process).

**Parameters:**
- `sleep_time` (datetime.timedelta) - Time interval between automatic backups

**Behavior:**
- Runs indefinitely in a loop
- Calls `create_backup()` at regular intervals
- Typically run in a separate process for non-blocking operation
- Useful for scheduled maintenance tasks

**Example:**
```python
import datetime
import backups

# Run backups every hour
interval = datetime.timedelta(hours=1)
backups.periodic_backup(interval)
```

---

## Error Responses

All error responses follow this standard format:

```json
{
  "error": "Error message describing what went wrong",
  "status": "error"
}
```

### HTTP Status Codes

| Code | Name | Common Cause |
|------|------|--------------|
| `200` | OK | Request successful |
| `400` | Bad Request | Missing or malformed request data, invalid placement code syntax |
| `401` | Unauthorized | Missing/invalid authentication token, insufficient permissions |
| `404` | Not Found | Inholder doesn't exist, image not found |
| `409` | Conflict | Inholder already exists, new placement code already in use |
| `500` | Internal Server Error | Unexpected server error during processing |

### Common Error Scenarios

**Missing Request Data (400):**
- Required fields not provided (e.g., missing `placement_code`, `name` in POST request)
- Query parameters not provided (e.g., missing `q` in search)

**Invalid Request Data (400):**
- Invalid placement code syntax (doesn't match pattern)
- Wrong data type for field (e.g., number where string expected)

**Unauthorized (401):**
- No JWT token provided in Authorization header
- JWT token is expired or invalid
- User lacks required permission for the operation

**Not Found (404):**
- Placement code doesn't exist in database
- Image file not found for the inholder
- User requested doesn't exist

**Conflict (409):**
- Attempting to add inholder that already exists
- Renaming to a placement code that's already in use

---

## Environment Variables

Configuration via `.env` file (auto-created on first run):

| Variable | Default | Description |
|----------|---------|-------------|
| `JWT_SECRET` | (auto-generated) | Secret key for signing JWT tokens. Auto-generated on first run if not set. Must be kept secret. |
| `ID` | (auto-generated) | Unique server identifier (UUID format). Auto-generated on first run. Used to identify this server instance. |
| `SERVER_NAME` | (not set) | Display name for the server. Used in beacon broadcast. |
| `PORT` | `5000` | Server listening port. Change to run multiple instances on different ports. |
| `BACKUP_INTERVAL_SECONDS` | `3600` | Time between automatic backups in seconds (default: 1 hour). |
| `BACKUP_FOLDER` | `backups` | Directory path for storing backup ZIP files. Created if it doesn't exist. |

**Notes:**
- The `.env` file is created in the server working directory on first run
- `JWT_SECRET` is critical for security - keep it confidential
- Changing `PORT` requires restarting the server
- Backup folder path can be relative or absolute

---

## Best Practices & Implementation Guide

### Authentication Flow

1. **Initial Login:** POST `/login` with username/password to get tokens
2. **Store Tokens:** Save both `access_token` (short-lived) and `refresh_token` (long-lived)
3. **Use Access Token:** Include access token in Authorization header for regular requests
4. **Token Refresh:** Before token expires, use `refresh_token` to get new tokens via POST `/refresh`
5. **Logout:** Use POST `/logout` with refresh token to revoke access

### Token Expiration Handling

- **Access tokens expire after 15 minutes** - Client should track expiration time
- **Refresh tokens expire after 24 hours** - User must log in again after 24 hours
- Implement automatic token refresh 1 minute before expiration
- On 401 response, attempt refresh; if refresh fails, redirect to login

### Search Best Practices

- **Use pagination** for large result sets: `max_results` and `skip_number`
- **Cache search results** on client for frequently repeated queries
- **Empty query** (`q=""`) returns all items - consider limiting with `max_results`
- **Use `only_leaves=true`** when searching for actual storage locations only
- Fuzzy matching is flexible - typos and partial matches work well

### Hierarchy Management

- **Plan your placement code structure** before bulk import
- **Parent must exist before child:** Cannot create "A-1-B" if "A-1" doesn't exist
- **Use meaningful codes:** "A-1" is better than "TEMP-X" for maintainability
- **Breadcrumb navigation:** Use `/trail` endpoint for UI navigation components
- **Recursive delete:** Remember `/remove` deletes all descendants

### Image Handling

- **Supported formats:** PNG, JPEG, HEIC, and most Pillow-supported formats
- **Images are converted to WebP** automatically for efficient storage
- **Recommended image sizes:**
  - Map images: 800x600 to 1920x1440 pixels
  - Description images: 600x400 to 1024x768 pixels
- **Image quality:** Default 85/100 (configurable via `IMAGE_QUALITY` config)
- **Always provide both images** for complete UI experience

### Error Handling

```python
# Example error handling pattern
import requests

try:
    response = requests.post('http://localhost:5000/add', 
        headers={'Authorization': f'Bearer {token}'},
        json={...})
    
    if response.status_code == 409:
        # Inholder already exists
        handle_conflict()
    elif response.status_code == 401:
        # Token expired or permission denied
        refresh_token_or_login()
    elif response.status_code == 400:
        # Invalid data
        show_validation_error(response.json())
    else:
        response.raise_for_status()
except requests.exceptions.RequestException as e:
    # Network error
    handle_network_error(e)
```

### Connection & Timeout Settings

- **Connection timeout:** Use 5-10 seconds
- **Read timeout:** Use 15-30 seconds (allows time for large database operations)
- **Retry policy:** Implement exponential backoff for network errors
- **Connection pooling:** Reuse connections for multiple requests

### Performance Tips

- **Use `/get_children/` for tree traversal** instead of loading all items
- **Cache inholder data** if not changing frequently
- **Batch multiple image uploads** into single requests where possible
- **Use `skip_number` for pagination** rather than filtering results client-side
- **Avoid repeated `/get_all` calls** - cache results with change tracking

### Multi-Server Deployment

- Use `/server_id` endpoint to identify which server client is connected to
- Different servers have different `ID` values (auto-generated UUIDs)
- Each server maintains independent database and user list
- Plan for server discovery mechanism using beacon broadcasts

---

## Data Models

### Inholder
Represents an item in the hierarchical storage system.

```python
{
  "placement_code": str,            # Hierarchical identifier (e.g., "A-1-B")
                                     # Empty string "" represents the root
                                     # Format: uppercase alphanumeric and hyphens only
  "name": str,                       # Display name (required)
  "description": str,                # Description text (optional)
  "keywords": str,                   # Searchable keywords, typically comma-separated (optional)
  "children_arrangement": str,       # Layout/arrangement setting for child items (optional)
  "self_alignment": str,             # Alignment setting for this item (optional)
  "color": str,                      # Color value for UI representation (optional)
  "has_map_image": bool,             # Whether a map/layout image is stored
  "has_description_image": bool      # Whether a description image is stored
}
```

**Placement Code Rules:**
- Must be uppercase alphanumeric ASCII and hyphens only
- Segments are separated by hyphens (e.g., `A`, `A-1`, `A-1-B`)
- Empty string is reserved for the root inholder
- Parent of placement code `A-1-B` is `A-1`

---

### User
Represents a user account with authentication and permissions.

```python
{
  "id": str,                    # Unique user identifier (UUID)
  "username": str,              # Username for login
  "permissions": list[str]      # List of granted permissions
                                 # Possible values: "add", "update", "remove", "rename_server"
}
```

**Note:** User passwords are hashed with werkzeug.security.generate_password_hash and never exposed in API responses.

---

### Permission System

Available permissions that can be assigned to users:

| Permission | Description |
|-----------|-------------|
| `"add"` | Can create new inholders via POST /add |
| `"update"` | Can modify existing inholders via PUT /update |
| `"remove"` | Can delete inholders via DELETE /remove |
| `"rename_server"` | Can update root inholder name via PUT /update_root |

---

# API Reference

This document summarizes the FastAPI endpoints exposed by the backend.

## Base URL

By default the server runs at <http://127.0.0.1:5000>. The convenience script uses port 5000.

## Authentication

Most mutating routes require authentication using a bearer token. The token is issued by /auth/login and should be sent as:

```http
Authorization: Bearer <token>
```

### POST /auth/login

Authenticate a user and receive an access token.

Request body must use form fields:

```text
username=<username>
password=<password>
```

Example:

```bash
curl -X POST http://127.0.0.1:5000/auth/login \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -d 'username=admin&password=secret'
```

Response:

```json
{"access_token":"...","token_type":"bearer"}
```

### GET /auth/authorized

Validates the current access token.

## User management

### POST /users/create

Create a user. Requires admin role.

Form fields: username, password, role.

### PUT /users/update

Update a user password or role. Requires admin role.

### DELETE /users/remove

Remove a user. Requires admin role.

### GET /users/get/all

List all users. Requires admin role.

### GET /users/get/me

Get the current authenticated user profile.

## Item and hierarchy routes

### GET /get/root

Get the root item. The root uses the empty placement code "".

### GET /get

Get an item by placement code.

Example:

```bash
curl http://127.0.0.1:5000/get?code=A
```

### GET /get/children

List child items for a parent placement code.

Example:

```bash
curl http://127.0.0.1:5000/get/children?code=A
```

### GET /get/children/root

List the root's child items.

### GET /get/all

Return all items. Add only_leaves=true to return only leaf nodes.

### GET /search

Search items by text.

Common query parameters:

- q: search string
- max_results: maximum number of results
- skip_number: offset for pagination
- only_leaves: only return leaves
- info_level: 0 for full item details, 1 for basic fields

### GET /trail

Return the breadcrumb trail for a placement code.

### GET /has_children

Check whether a placement code has children.

## Item mutation routes

### POST /add

Create a new item. Requires admin or maintainer role.

Form fields include placement_code, name, description, keywords, children_arrangement, self_alignment, color, map_image, and desc_image.

### DELETE /remove

Delete one or more items. The form field codes accepts a list of placement codes. Requires admin or maintainer role.

### PUT /update/root

Update the root item. Requires admin, maintainer, or editor role.

### PUT /update

Update an item by placement code. Requires admin, maintainer, or editor role.

## Image routes

### GET /descimage/root

Get the description image for the root item.

### GET /mapimage/root

Get the map image for the root item.

### GET /descimage

Get the description image for a specific placement code.

### GET /mapimage

Get the map image for a specific placement code.

## Utility routes

### GET /id

Return the server identifier.

### GET /ping

Health check endpoint.

## Backup routes

### GET /backups/get/all

List available backups. Requires admin role.

### POST /backups/dump

Create a new backup immediately. Requires admin role.

### POST /backups/schedule_restore

Schedule a restore from a backup ID. Requires admin role. The restore is applied on the next startup.

### DELETE /backups/remove

Delete a backup archive. Requires admin role.

## Settings routes

### GET /settings/get

Read a setting by ID.

### PUT /settings/update

Update settings such as image_quality, max_backups_size, and backup_interval_seconds. Requires admin role.

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

# Skapersøk Backend

Skapersøk Backend is a FastAPI service for managing a hierarchical item database with authentication, image storage, search, and automated backups.

## What the backend provides

- A hierarchical item model with placement codes
- Full-text search over item metadata
- Authentication and role-based access control
- Image support for map and description images
- Backup creation, restore scheduling, and periodic backup handling
- A browsable API at /docs

## Quick start

### 1. Prerequisites

- Python 3.10 or newer
- pip available
- A shell with access to the repository

### 2. Create and activate a virtual environment

Linux / macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Windows (PowerShell):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate
```

### 3. Install dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Create the environment file

The application reads configuration from config/.env. A starter file is created automatically, but you should set at least a strong JWT secret before running the server.

Example:

```dotenv
JWT_SECRET=replace-this-with-a-long-random-secret
```

### 5. Initialize the database and create the first admin user

Run:

```bash
python3 setup.py
```

The setup script initializes the SQLite databases and prompts for the first admin username and password.

### 6. Start the server

The repository includes a convenience script:

```bash
./start.sh
```

You can also run it directly:

```bash
fastapi run --host 0.0.0.0 --port 5000 main.py
```

The server will start on <http://127.0.0.1:5000>.

### 7. Verify the server

```bash
curl http://127.0.0.1:5000/ping
```

Expected response:

```json
{"message":"pong"}
```

## Main modules

- main.py: FastAPI app, route definitions, and startup lifecycle
- auth.py: authentication, JWT handling, and user roles
- database.py: item CRUD, validation, and image path handling
- search.py: full-text search logic
- backups.py: backup creation and restore scheduling
- dbmigrator.py and itemdbmigrator.py: schema migration support
- settings.py and paths.py: environment and filesystem configuration

## Documentation

- docs/APIReference.md: API route overview and examples
- docs/DatabaseSetup.md: environment variables and setup tips
- docs/DatabaseLayout.md: SQLite tables and persisted data layout
- docs/PlacementCode.md: placement code rules and examples
- docs/Backups.md: backup system behavior and routes
- docs/Gridsystem.md: layout behavior for children and self-alignment
- docs/ProjectStructure.md: architectural overview of the backend modules

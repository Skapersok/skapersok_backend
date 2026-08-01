# Skapersøk Backend

Skapersøk Backend is a FastAPI service for managing a hierarchical item database with authentication, image storage, search, and automated backups.

## What the backend provides

- A hierarchical item model with placement codes
- Full-text search over item metadata
- Authentication and role-based access control
- Image support for map and description images
- Backup creation, restore scheduling, and periodic backup handling
- A browsable API at /docs
- LAN discovery beacon (UDP, port 50000) so clients can auto-find the server

## Quick start (Docker — recommended)

This is the fastest path to a running server and the one we recommend for production and for anyone self-hosting.

### 1. Prerequisites

- Docker and Docker Compose installed
- Linux host recommended (see note on the discovery beacon below)

### 2. Clone the repository

```bash
git clone https://github.com/yourname/skapersok-backend
cd skapersok-backend
```

### 3. Start the server

On **Linux**:

```bash
docker compose up -d
```

On **Windows**:

```bash
docker compose -f docker-compose.yml -f docker-compose.windows.yml up -d
```

This builds the image, creates the `data/` and `config/` folders on first run, and starts the server. On first boot, the app generates its own `config/.env` with a random `JWT_SECRET` and instance `ID` — no manual setup needed to get running.

Check it's healthy:

```bash
docker compose ps
curl http://localhost:5000/ping
```

### 4. Set a few things before going to production

While the server runs fine out of the box, review `config/.env` and set values explicitly rather than relying on defaults — particularly `JWT_SECRET` if you're migrating from an existing install (see below).

### 5. Updating

```bash
git pull
docker compose build
docker compose up -d
```

Editing `config/.env` only (no code change) just needs:

```bash
docker compose up -d
```

No rebuild required — config changes take effect on container restart.

### What persists across restarts and rebuilds

- `./data` — databases, images, backups
- `./config` — `.env` settings, including your JWT secret and instance ID

Both are bind-mounted from the host, so `docker compose down` and even `docker compose build` will not touch them. Only deleting these folders yourself will reset the app to a fresh state.

### A note on the discovery beacon

The beacon (UDP, port 50000) is used for LAN auto-discovery by clients. It requires host networking to work reliably, which our `docker-compose.yml` enables via `network_mode: host`. This means:

- **Linux hosts:** works out of the box, identical to running the app directly.
- **Docker Desktop on Mac/Windows:** host networking is not supported the same way, so LAN discovery will not work in these environments. The rest of the app is unaffected — clients can still connect by entering the server's address manually.

If you're self-hosting on a Linux VPS or home server, you don't need to do anything extra here.

## Quick start (manual, without Docker)

Useful for local development or if you'd rather not use Docker.

### 1. Prerequisites

- Python 3.12 or newer
- [uv](https://docs.astral.sh/uv/) (recommended) or plain `pip`

### 2. Install dependencies

With `uv` (recommended — also creates the virtual environment for you):

```bash
uv sync
```

With plain `pip`:

```bash
python3 -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\Activate
pip install --upgrade pip
pip install .
```

### 3. Configuration

The application reads settings from `config/.env`. This file is created automatically on first run, with a randomly generated `JWT_SECRET` and instance `ID` — you don't need to create it by hand. If you want to set values ahead of time, create `config/.env` yourself before first launch:

```dotenv
JWT_SECRET=replace-this-with-a-long-random-secret
IMAGE_QUALITY=85
ACCESS_TOKEN_EXPIRE_MINUTES=60
MAX_BACKUPS_SIZE=1000000000
BACKUP_INTERVAL_SECONDS=3600
AUTOOPEN_BROWSER=true
```

Only `JWT_SECRET` needs attention; everything else has a sensible default.

### 4. Start the server

```bash
uv run python main.py
```

or, with plain pip and an activated venv:

```bash
python main.py
```

This runs startup checks (folder creation, config bootstrap), starts the discovery beacon, and launches the API. By default it also opens your browser to the running instance — set `AUTOOPEN_BROWSER=false` in `config/.env` to disable this (this is already disabled automatically inside Docker).

The server starts on <http://127.0.0.1:5000>.

### 5. Verify the server

```bash
curl http://127.0.0.1:5000/ping
```

Expected response:

```json
{"status": "ok"}
```

## Running on server startup (Docker)

`docker-compose.yml` sets `restart: unless-stopped`, so the container will automatically restart after a crash or a host reboot — as long as Docker itself starts on boot and the container was left running (not manually stopped) beforehand.

To make sure Docker itself starts on boot (most installs do this already):

```bash
sudo systemctl enable docker
```

## Main modules

- `main.py`: unified entry point (startup checks, beacon, server)
- `routing.py`: FastAPI app, route definitions, and startup lifecycle
- `auth.py`: authentication, JWT handling, and user roles
- `database.py`: item CRUD, validation, and image path handling
- `search.py`: full-text search logic
- `backups.py`: backup creation and restore scheduling
- `dbmigrator.py` and `itemdbmigrator.py`: schema migration support
- `settings.py` and `paths.py`: environment and filesystem configuration
- `beacon.py`: UDP discovery beacon for LAN client auto-detection

# Building executables
Skapersøk Backend can be built into a standalone executable using [PyInstaller](https://www.pyinstaller.org/). To make this process easier and more reproducible, you can use the `skapersok_backend.spec` file. Simply run the following command in the project root:

```bash
pyinstaller skapersok_backend.spec
```

## License

Skapersøk Backend is licensed under the GNU Affero General Public License v3.0 (AGPL-3.0). See `LICENSE` for the full text.

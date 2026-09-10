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

## Starting the server

See [the docs](https://docs.skapersok.no/getting_started/server_setup/) for setup guides.

## Running on server startup (Docker)

`docker-compose.yml` sets `restart: unless-stopped`, so the container will automatically restart after a crash or a host reboot — as long as Docker itself starts on boot and the container was left running (not manually stopped) beforehand.

To make sure Docker itself starts on boot (most installs do this already):

```bash
sudo systemctl enable docker
```

## Building executables

Skapersøk Backend can be built into a standalone executable using [PyInstaller](https://www.pyinstaller.org/). To make this process easier and more reproducible, you can use the `skapersok_backend.spec` file. Simply run the following command in the project root:

```bash
pyinstaller skapersok_backend.spec
```

## Automatic release builder

If a commit is pushed with a version tag, github actions will attempt to make a release if that tag matches the current version tag in `pyproject.toml`.

To use this feature, add a tag to your commit like this:
"v" + [`pyproject.toml` version number]

So a version of "0.4.0b1" inside `pyproject.toml` should be tagged as "v0.4.0b1".

## License

Skapersøk Backend is licensed under the GNU Affero General Public License v3.0 (AGPL-3.0). See `LICENSE` for the full text.

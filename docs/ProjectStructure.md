# Project Structure & Development Guide

This repository contains the backend service for Skapersøk. The code is organized around FastAPI routes, authentication, SQLite persistence, search, image handling, and backup management.

## High-level layout

```text
.
├── auth.py               # Authentication, JWTs, role checks, user storage
├── backups.py            # Backup creation, restore scheduling, cleanup
├── database.py           # Item CRUD, validation, image paths, and helpers
├── dbmigrator.py         # Entry point for database schema migration
├── itemdbmigrator.py     # Item database schema versioning
├── main.py               # FastAPI application and route definitions
├── paths.py              # Path constants for data, config, backups, temp
├── search.py             # Search implementation for full-text indexing
├── settings.py           # Environment-backed settings helpers
├── setup.py              # Initial setup script for first admin user
├── start.sh              # Convenience launcher for the app
├── config/               # Runtime configuration and .env file
├── data/                 # Persistent data including SQLite files and images
├── docs/                 # Project documentation
└── temp/                 # Temporary working directory
```

## Core modules

### main.py

The FastAPI application entry point. It defines the API routes for authentication, item access, search, images, backups, and settings.

### auth.py

Handles login, token creation, user lookup, password hashing, and role-based access. The supported roles are admin, maintainer, editor, and viewer.

### database.py

Contains the logic for interacting with the SQLite item database. It manages validation of placement codes, parent-child relationships, image storage, and item updates/removals.

### search.py

Provides the search backend used by the /search endpoint. The application uses SQLite FTS5 for indexed text search.

### backups.py

Responsible for creating zip backups of the data directory, cleaning up old archives, and scheduling automatic restores on startup.

### paths.py and settings.py

Provide centralized filesystem and environment configuration. These modules define where the SQLite files, images, config, and backups live.

## Runtime data layout

The application uses the following persistent locations:

- data/data/database.db: item database
- data/data/users.db: user database
- data/data/img/mapimgs/: map images
- data/data/img/descimgs/: description images
- data/backups/: zip backup archives
- config/.env: runtime settings

## Development notes

- Most application logic should stay in the module that matches its responsibility.
- Route handlers in main.py should stay concise and delegate to auth.py, database.py, backups.py, or search.py when possible.
- The startup lifecycle in main.py performs migrations, applies scheduled restore actions, starts backup handling, and starts the beacon service.
- For local development, use the setup script once and then start the server with start.sh or fastapi run.

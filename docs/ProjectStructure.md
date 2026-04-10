# Project Structure & Development Guide

This document outlines the architectural structure of the Shelfsearch application following the refactoring to a modular, type-based architecture.

## Overview

The application is built using [Flet](https://flet.dev/) (Python) and follows a separation-of-concerns pattern. The codebase is organized into distinct layers: **Models** (Data), **Services** (Logic/Networking), and **UI** (Views & Components).

## Directory Structure

The source code is located in the `src/` directory.

```text
src/
├── main.py                 # Application entry point and routing configuration
├── styles.py               # Centralized styling constants (Colors, Sizes, Fonts)
├── models/                 # Pure data classes and business logic entities
│   ├── location.py         # Location, DrawPoint, DrawPointsHandler
│   ├── search.py           # SearchSettings
│   └── user.py             # UserInformation
├── services/               # External communication and application services
│   ├── api.py              # DatabaseCommunicator, Server API wrapper
│   └── discovery.py        # UDP Broadcast client for server discovery
├── ui/                     # User Interface code
│   ├── components/         # Reusable UI widgets
│   │   ├── connecting.py   # Connection status indicators
│   │   ├── editor.py       # Editor-specific tools (DrawCanvas, etc.)
│   │   ├── forms.py        # Input forms and dialogs
│   │   └── search.py       # Search bar and result lists
│   └── views/              # Full-page layouts
│       ├── editor.py       # Location editor page
│       ├── home.py         # Landing/Home page
│       └── search.py       # Main search interface page
└── utils/                  # Helper functions
    └── images.py           # Image processing utilities
```

## Module Details

### 1. Models (`src/models/`)
Contains the core data structures used throughout the app. These classes are generally decoupled from the UI.
- **`Location`**: Represents a physical location/shelf, including placement codes and coordinates.
- **`DrawPoint`**: Represents a point on the map editor canvas.

### 2. Services (`src/services/`)
Handles all "backend" logic and networking.
- **`api.py`**: Contains `DatabaseCommunicator` for HTTP requests to the backend server.
- **`discovery.py`**: Handles the UDP broadcast mechanism to automatically find the server on the local network.

### 3. UI (`src/ui/`)
Split into **Views** (Pages) and **Components** (Widgets).
- **Views**: Correspond to routes (e.g., `/`, `/search`, `/edit`). They assemble components into a full screen.
- **Components**: Small, reusable pieces of UI (e.g., `LocationCard`, `SearchField`).

### 4. Styles (`src/styles.py`)
A single source of truth for design tokens.
- **`Colors`**: Application color palette.
- **`Sizes`**: Standardized dimensions (padding, font sizes, icon sizes).
- **`Fonts`**: Font family definitions.

## Routing

Routing is handled in `src/main.py`. The application uses Flet's routing system to navigate between views:
- `/`: Home Page
- `/search/:url`: Search Page (connected to a specific server URL)
- `/search/:url/edit`: Editor Page

## Development Guidelines

- **Imports**: Use absolute imports from `src` root where possible, or relative imports within modules.
  - Example: `import models.location as loc_md`
- **State Management**: State is currently managed within individual components or passed down via parameters.
- **Adding New Features**:
  1. Define data structures in `models/`.
  2. Implement logic in `services/` if needed.
  3. Create reusable widgets in `ui/components/`.
  4. Assemble them in a view in `ui/views/`.

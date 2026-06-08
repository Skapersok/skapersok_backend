# Skapersøk Backend

## Setup Guide

### Prerequisites

- Python 3.10 or newer
- `pip` available
- Recommended: create a virtual environment before installing dependencies

### 1. Create and activate a virtual environment (recommended)

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

Windows (Command Prompt):

```cmd
python -m venv .venv
\.venv\Scripts\activate.bat
```

### 2. Install dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Initialize the database and create the first user

Run the setup script and follow the prompts:

Linux / macOS:

```bash
python3 setup.py
```

Windows:

```powershell
python setup.py
```

The script creates the required database files and asks for the first admin username and password.

### 4. Start the server

Run the backend using the provided `main.py` entrypoint:

Linux / macOS / Windows:

```bash
fastapi run --host 0.0.0.0 --port 5000 main.py
```

This starts the FastAPI application on `http://127.0.0.1:5000`.

### 5. Verify the server is running

Open a browser or use `curl`:

```bash
curl http://127.0.0.1:5000/ping
```

Expected response:

```json
{"message":"pong"}
```


"""Module for managing application settings stored in a .env file."""

import paths
import uuid
import secrets
import string


def _load_env() -> dict[str, str | bool]:
    """Load the .env file into a dictionary."""
    env: dict[str, str | bool] = {}
    if not paths.DOTENV_PATH.exists():
        paths.DOTENV_PATH.parent.mkdir(parents=True)
        paths.DOTENV_PATH.touch(exist_ok=True)
        return env

    with paths.DOTENV_PATH.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                # Key with value
                key, value = line.split("=", 1)
                env[key.strip()] = value.strip()
            else:
                # Flag-only key
                env[line] = True

    return env


def _write_env(env: dict[str, str | bool]) -> None:
    """Write the dictionary back to the .env file."""
    with paths.DOTENV_PATH.open("w", encoding="utf-8") as f:
        for k, v in env.items():
            if v is True:
                # Flag-only key
                f.write(f"{k}\n")
            else:
                # Key with value
                f.write(f"{k}={v}\n")


def get(key: str, default: str | bool | None = None) -> str | bool | None:
    """Get a value from the .env file. If the key does not exist and default is provided, write default to the file and return default."""
    env = _load_env()
    stored_value = env.get(key, None)

    if stored_value is not None:
        return stored_value

    if default is not None:
        if not isinstance(default, bool):
            default = str(default)

        env[key] = default
        _write_env(env)
        return default

    # Default is None and key not found
    return None


def set(key: str, value: str | bool = True) -> None:
    """Set or update a value in the .env file."""
    env = _load_env()
    env[key] = value
    _write_env(env)


def delete(key: str) -> None:
    """Remove a key from the .env file."""
    env = _load_env()
    if key in env:
        del env[key]
        _write_env(env)


def isset(key: str) -> bool:
    """Check if a key exists in the .env file."""
    env = _load_env()
    return key in env.keys()


# === Default settings ===
try:
    BACKUP_INTERVAL_SECONDS = int(get("BACKUP_INTERVAL_SECONDS", "3600"))
except:
    raise ValueError(
        "Invalid value for BACKUP_INTERVAL_SECONDS in .env. It should be an integer."
    )

JWT_SECRET = str(
    get(
        "JWT_SECRET",
        "".join(
            secrets.choice(string.ascii_lowercase + string.digits) for _ in range(40)
        ),
    )
)

try:
    uuid_string = get("ID", str(uuid.uuid4()))
    _ = uuid.UUID(uuid_string, version=4)
except:
    set("ID", str(uuid.uuid4()))
finally:
    ID = str(get("ID", str(uuid.uuid4())))

try:
    IMAGE_QUALITY = int(get("IMAGE_QUALITY", "85"))
except:
    raise ValueError(
        "Invalid value for IMAGE_QUALITY in .env. It should be an integer."
    )

PORT = 5000

try:
    ACCESS_TOKEN_EXPIRE_MINUTES = int(get("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
except:
    raise ValueError(
        "Invalid value for ACCESS_TOKEN_EXPIRE_MINUTES in .env. It should be an integer."
    )

MAX_BACKUPS_SIZE = int(get("MAX_BACKUPS_SIZE", "1000000000"))

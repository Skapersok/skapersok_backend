import secrets
import string
import uuid

from pydantic_settings import BaseSettings, SettingsConfigDict

import paths


def _generate_secret(length: int = 40) -> str:
    alphabet = string.ascii_lowercase + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))


def ensure_env_defaults() -> None:
    """Guarantee config/.env exists and has a stable JWT_SECRET / ID.
    Runs once at startup; does nothing on subsequent runs once these
    are already present on disk."""
    paths.CONFIG_FOLDER.mkdir(parents=True, exist_ok=True)
    paths.ensure_exists()
    env_path = paths.DOTENV_PATH

    existing: dict[str, str] = {}
    if env_path.exists():
        for line in env_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                existing[k.strip()] = v.strip()

    changed = False
    if "JWT_SECRET" not in existing:
        existing["JWT_SECRET"] = _generate_secret()
        changed = True
    if "ID" not in existing:
        existing["ID"] = str(uuid.uuid4())
        changed = True

    if changed:
        with env_path.open("w", encoding="utf-8") as f:
            for k, v in existing.items():
                f.write(f"{k}={v}\n")


def write_setting(key: str, value) -> None:
    """Persist one setting to config/.env. Takes effect after restart."""
    env_path = paths.DOTENV_PATH
    lines = (
        env_path.read_text(encoding="utf-8").splitlines() if env_path.exists() else []
    )
    existing = dict(
        line.split("=", 1)
        for line in lines
        if line and not line.startswith("#") and "=" in line
    )
    existing[key.upper()] = str(value)
    with env_path.open("w", encoding="utf-8") as f:
        for k, v in existing.items():
            f.write(f"{k}={v}\n")

            # config.py (additions)


ALLOWED_SETTINGS = {
    "image_quality": "image_quality",
    "max_backups_size": "max_backups_size",
    "backup_interval_seconds": "backup_interval_seconds",
    "autoopen_browser": "autoopen_browser",
}


def get_setting(name: str):
    """Read a currently-active setting value (from the loaded Settings object,
    i.e. reflects what's in effect since the last restart)."""
    if name not in ALLOWED_SETTINGS:
        raise KeyError(f"{name!r} is not an allowed setting")
    return getattr(settings, ALLOWED_SETTINGS[name])


def set_setting(name: str, value) -> None:
    """Validate and persist a new value for an allowed setting.
    Takes effect on next restart — does not mutate the running `settings` object."""
    if name not in ALLOWED_SETTINGS:
        raise KeyError(f"{name!r} is not an allowed setting")

    field_name = ALLOWED_SETTINGS[name]

    # Validate the new value against the Settings schema before writing it,
    # by re-validating a copy with just this field overridden. This reuses
    # Pydantic's type coercion/validation instead of hand-rolling casts,
    # and catches bad input (e.g. "banana" for an int) before it ever hits disk.
    candidate = settings.model_copy(update={field_name: value})
    Settings.model_validate(candidate.model_dump())

    env_key = field_name.upper()
    write_setting(env_key, getattr(candidate, field_name))


def list_settings() -> dict:
    """Return all allowed settings and their current values — handy for a
    GET /settings endpoint that populates an admin UI."""
    return {name: get_setting(name) for name in ALLOWED_SETTINGS}


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(paths.DOTENV_PATH),
        extra="ignore",
    )

    jwt_secret: str
    id: str
    image_quality: int = 85
    access_token_expire_minutes: int = 60
    max_backups_size: int = 1_000_000_000
    backup_interval_seconds: int = 3600
    autoopen_browser: bool = True
    port: int = 5000


ensure_env_defaults()
settings = Settings()

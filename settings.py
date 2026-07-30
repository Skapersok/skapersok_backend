"""Module for managing application settings stored in a .env file."""

import paths
import uuid
import secrets
import string


class Settings:
    ALLOWED_SETTINGS = {
        "image_quality": ("IMAGE_QUALITY", int),
        "max_backups_size": ("MAX_BACKUPS_SIZE", int),
        "backup_interval_seconds": ("BACKUP_INTERVAL_SECONDS", int),
        "autoopen_browser": ("AUTOOPEN_BROWSER", bool)
    }

    def __init__(self):
        # JWT_SECRET
        self.JWT_SECRET: str = str(
            self.get(
                "JWT_SECRET",
                "".join(
                    secrets.choice(string.ascii_lowercase + string.digits)
                    for _ in range(40)
                ),
            )
        )

        # ID
        try:
            uuid_string = self.get("ID", str(uuid.uuid4()))
            uuid.UUID(uuid_string, version=4)
        except Exception:
            self.set("ID", str(uuid.uuid4()))
        self.ID: str = str(self.get("ID"))

        # IMAGE_QUALITY
        try:
            self.IMAGE_QUALITY: int = int(self.get("IMAGE_QUALITY", "85"))
        except (TypeError, ValueError):
            raise ValueError(
                "Invalid value for IMAGE_QUALITY in .env. Must be an integer."
            )

        # PORT (constant, not stored in .env)
        self.PORT: int = 5000

        # ACCESS_TOKEN_EXPIRE_MINUTES
        try:
            self.ACCESS_TOKEN_EXPIRE_MINUTES: int = int(
                self.get("ACCESS_TOKEN_EXPIRE_MINUTES", "60")
            )
        except (TypeError, ValueError):
            raise ValueError(
                "Invalid value for ACCESS_TOKEN_EXPIRE_MINUTES in .env. Must be an integer."
            )

        # MAX_BACKUPS_SIZE
        self.MAX_BACKUPS_SIZE: int = int(self.get("MAX_BACKUPS_SIZE", "1000000000"))

        # BACKUP_INTERVAL_SECONDS
        try:
            self.BACKUP_INTERVAL_SECONDS: int = int(
                self.get("BACKUP_INTERVAL_SECONDS", "3600")
            )
        except (TypeError, ValueError):
            raise ValueError(
                "Invalid value for BACKUP_INTERVAL_SECONDS in .env. Must be an integer."
            )

        self.AUTOOPEN_BROWSER: bool = bool(self.get("AUTOOPEN_BROWSER", True))

    # === .env I/O ===

    def _load_env(self) -> dict[str, str | bool]:
        env: dict[str, str | bool] = {}
        if not paths.DOTENV_PATH.exists():
            paths.DOTENV_PATH.parent.mkdir(parents=True, exist_ok=True)
            paths.DOTENV_PATH.touch(exist_ok=True)
            return env
        with paths.DOTENV_PATH.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" in line:
                    key, value = line.split("=", 1)
                    env[key.strip()] = value.strip()
                else:
                    env[line] = True
        return env

    def _write_env(self, env: dict[str, str | bool]) -> None:
        with paths.DOTENV_PATH.open("w", encoding="utf-8") as f:
            for k, v in env.items():
                f.write(f"{k}\n" if v is True else f"{k}={v}\n")

    # === Low-level key access ===

    def get(self, key: str, default: str | bool | None = None) -> str | bool | None:
        env = self._load_env()
        stored = env.get(key)
        if stored is not None:
            return stored
        if default is not None:
            env[key] = default if isinstance(default, bool) else str(default)
            self._write_env(env)
            return default
        return None

    def set(self, key: str, value: str | bool = True) -> None:
        env = self._load_env()
        env[key] = value
        self._write_env(env)

    def delete(self, key: str) -> None:
        env = self._load_env()
        if key in env:
            del env[key]
            self._write_env(env)

    def isset(self, key: str) -> bool:
        return key in self._load_env()

    # === Named-setting API ===

    def get_setting(self, name: str):
        if name not in self.ALLOWED_SETTINGS:
            raise KeyError(name)
        env_key, cast = self.ALLOWED_SETTINGS[name]
        return cast(self.get(env_key))

    def set_setting(self, name: str, value) -> None:
        if name not in self.ALLOWED_SETTINGS:
            raise KeyError(name)
        env_key, cast = self.ALLOWED_SETTINGS[name]
        self.set(env_key, str(cast(value)))


settings = Settings()

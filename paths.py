from pathlib import Path

# Base folder for your project (directory of this file)

# Persistent data folder (inside Docker volume)
USER_DATA = Path("data")
DATA_FOLDER_PATH = USER_DATA / "data"
DATABASE_PATH = DATA_FOLDER_PATH / "database.db"
USERBASE_PATH = DATA_FOLDER_PATH / "users.db"
CUSTOM_VALUE_TYPES = DATA_FOLDER_PATH / "custom_value_types.db"

# Image folders (inside data)
IMAGE_FOLDER = DATA_FOLDER_PATH / "img"
MAP_IMAGE_FOLDER = IMAGE_FOLDER / "mapimgs"
DESCRIPTION_IMAGE_FOLDER = IMAGE_FOLDER / "descimgs"

# Config folder (inside Docker volume)
CONFIG_FOLDER = Path("config")

# Backup folder (inside data)
BACKUP_FOLDER = USER_DATA / "backups"

# Environment variables
DOTENV_PATH = CONFIG_FOLDER / ".env"

# Temporary folder (ephemeral)
TEMP_FOLDER = Path("temp")


def ensure_exists() -> None:
    """
    Ensure all necessary folders exist.
    - DATA_FOLDER_PATH and its subfolders are persisted as a Docker volume.
    - TEMP_FOLDER is ephemeral, created inside the container.
    """
    for folder in (
        DATA_FOLDER_PATH,
        MAP_IMAGE_FOLDER,
        DESCRIPTION_IMAGE_FOLDER,
        TEMP_FOLDER,
        CONFIG_FOLDER,
        BACKUP_FOLDER,
    ):
        folder.mkdir(parents=True, exist_ok=True)

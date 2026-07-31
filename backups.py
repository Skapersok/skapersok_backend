import shutil
import time
import uuid
import paths
from pathlib import Path
from settings import settings
import json
from datetime import datetime, timezone

PENDING_RESTORE_PATH = paths.CONFIG_FOLDER / "pending_restore.json"
FAILED_RESTORE_PATH = paths.CONFIG_FOLDER / "pending_restore.failed.json"


TIMESTAMP_FILE_FORMAT = "%Y-%m-%dT%H-%M-%S.%f"


def _list_backup_names() -> list[str]:
    backup_folder = paths.BACKUP_FOLDER

    if not backup_folder.exists():
        return []

    names = []

    for file in backup_folder.iterdir():
        if file.is_file() and file.suffix == ".zip":
            names.append(file.stem)

    return names


class BackupInfo:
    def __init__(self, id: str, timestamp: datetime):
        self.id = id
        self.timestamp = timestamp
        self.name = self.timestamp.strftime(TIMESTAMP_FILE_FORMAT) + " " + self.id

        archive_path = paths.BACKUP_FOLDER / (self.name + ".zip")
        if archive_path.exists():
            self.size = archive_path.stat().st_size
        else:
            self.size = None

    @staticmethod
    def from_name(name: str):
        timestamp_str, id = name.split(" ", 1)

        timestamp = datetime.strptime(
            timestamp_str, TIMESTAMP_FILE_FORMAT
        )  # new format

        return BackupInfo(id=id, timestamp=timestamp)

    @staticmethod
    def from_id(id: str):
        timestamp = None

        for name in _list_backup_names():
            timestamp_str, _id = name.split(" ", 1)
            if id == _id:
                timestamp = datetime.strptime(timestamp_str, TIMESTAMP_FILE_FORMAT)

        if not timestamp:
            return None

        return BackupInfo(id, timestamp)


def _write_json_atomic(path: Path, payload: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = path.with_suffix(path.suffix + ".tmp")
    with temp_path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=True, indent=2)
    temp_path.replace(path)


def schedule_restore(info: BackupInfo, requested_by: str | None = None) -> None:
    payload = {
        "backup_id": info.id,
        "requested_at": datetime.now(timezone.utc).isoformat(),
        "requested_by": requested_by,
    }
    _write_json_atomic(PENDING_RESTORE_PATH, payload)


def get_scheduled_restore() -> dict | None:
    if not PENDING_RESTORE_PATH.exists():
        return None
    with PENDING_RESTORE_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)


def clear_scheduled_restore() -> None:
    if PENDING_RESTORE_PATH.exists():
        PENDING_RESTORE_PATH.unlink()


def apply_scheduled_restore() -> bool:
    pending = get_scheduled_restore()
    if pending is None:
        return False

    backup_id = pending.get("backup_id")
    if not isinstance(backup_id, str):
        _write_json_atomic(
            FAILED_RESTORE_PATH, {"error": "Invalid backup_id", "pending": pending}
        )
        clear_scheduled_restore()
        return False

    info = BackupInfo.from_id(backup_id)
    if info is None:
        _write_json_atomic(
            FAILED_RESTORE_PATH, {"error": "Backup not found", "pending": pending}
        )
        clear_scheduled_restore()
        return False

    _restore_backup(info)
    clear_scheduled_restore()
    return True


def periodic_backup():
    """
    Run periodic backups. This function halts the thread.
    """
    try:
        while True:
            time.sleep(settings.backup_interval_seconds)
            dump()
    except KeyboardInterrupt:
        pass


def all_backups() -> list[BackupInfo]:
    backups = []

    for name in _list_backup_names():
        backups.append(BackupInfo.from_name(name))

    return backups


def remove_backup(info: BackupInfo):
    backup_folder = paths.BACKUP_FOLDER
    archive_path = backup_folder / (info.name + ".zip")

    if archive_path.exists():
        archive_path.unlink()


def _restore_backup(info: BackupInfo):
    backup_folder = paths.BACKUP_FOLDER
    archive_path = backup_folder / (info.name + ".zip")

    if not archive_path.exists():
        return

    if paths.DATA_FOLDER_PATH.exists():
        shutil.rmtree(paths.DATA_FOLDER_PATH)

    shutil.unpack_archive(str(archive_path), str(paths.DATA_FOLDER_PATH))


def _remove_old_backups_to_fit_max_size():
    """
    Removes backups so that they do not surpass the maximum size set in the settings.
    """
    backups = all_backups()
    backups.sort(key=lambda b: b.timestamp, reverse=True)

    total_size = 0

    for b in backups:
        if not b.size:
            continue

        total_size += b.size
        if total_size > settings.max_backups_size:
            remove_backup(b)


def create_backup(info: BackupInfo):
    backup_folder = paths.BACKUP_FOLDER

    if not backup_folder.exists():
        backup_folder.mkdir(parents=True, exist_ok=True)

    if not paths.DATA_FOLDER_PATH.exists():
        return

    basename = info.name

    archive_path = backup_folder / basename
    counter = 0

    while Path(str(archive_path) + ".zip").exists():
        counter += 1
        archive_path = backup_folder / (basename + " " + str(counter))

    shutil.make_archive(str(archive_path), "zip", paths.DATA_FOLDER_PATH)

    _remove_old_backups_to_fit_max_size()


def dump():
    """
    Create a backup of the database in its current state.

    Note! If there is no database, no backup is created.
    """
    now = datetime.now()
    id = uuid.uuid4().hex

    info = BackupInfo(id=id, timestamp=now)

    create_backup(info)

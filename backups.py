import shutil
import time
import datetime
import uuid
import paths
from pathlib import Path
import settings


class BackupInfo:
    def __init__(self, id: str, timestamp: datetime.datetime):
        self.id = id
        self.timestamp = timestamp

    def name(self) -> str:
        return self.timestamp.isoformat() + " " + self.id

    def create_from_name(name: str):
        timestamp_str, id = name.split(" ", 1)
        timestamp = datetime.datetime.fromisoformat(timestamp_str)
        return BackupInfo(id=id, timestamp=timestamp)

    def size(self) -> int:
        backup_folder = paths.BACKUP_FOLDER
        archive_path = backup_folder / (self.name() + ".zip")
        if archive_path.exists():
            return archive_path.stat().st_size
        return 0


def periodic_backup():
    """
    Run periodic backups. This function halts the thread.
    """
    try:
        while True:
            time.sleep(settings.BACKUP_INTERVAL_SECONDS)
            create_backup()
    except KeyboardInterrupt:
        pass


def all_backups() -> list[BackupInfo]:
    backup_folder = paths.BACKUP_FOLDER

    if not backup_folder.exists():
        return []

    backups = []

    for file in backup_folder.iterdir():
        if file.is_file() and file.suffix == ".zip":
            name = file.stem
            backups.append(BackupInfo.create_from_name(name))

    return backups


def remove_backup(info: BackupInfo):
    backup_folder = paths.BACKUP_FOLDER
    archive_path = backup_folder / (info.name() + ".zip")

    if archive_path.exists():
        archive_path.unlink()


def restore_backup(info: BackupInfo):
    backup_folder = paths.BACKUP_FOLDER
    archive_path = backup_folder / (info.name() + ".zip")

    if not archive_path.exists():
        return

    if paths.DATA_FOLDER_PATH.exists():
        shutil.rmtree(paths.DATA_FOLDER_PATH)

    shutil.unpack_archive(str(archive_path), str(paths.DATA_FOLDER_PATH))


def create_backup(info: BackupInfo):
    backup_folder = paths.BACKUP_FOLDER

    if not backup_folder.exists():
        backup_folder.mkdir()

    if not paths.DATA_FOLDER_PATH.exists():
        return

    basename = info.name()

    archive_path = backup_folder / basename
    counter = 0

    while Path(str(archive_path) + ".zip").exists():
        counter += 1
        archive_path = backup_folder / (basename + " " + str(counter))

    shutil.make_archive(str(archive_path), "zip", paths.DATA_FOLDER_PATH)


def dump():
    """
    Create a backup of the database in its current state.

    Note! If there is no database, no backup is created.
    """
    now = datetime.datetime.now()
    id = uuid.uuid4().hex

    info = BackupInfo(id=id, timestamp=now)

    create_backup(info)

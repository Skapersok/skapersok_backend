import shutil
import time
import datetime
import paths
from pathlib import Path
import settings


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


def create_backup(prefix: str | None = None):
    """
    prefix: the prefix of the database name.

    Create a backup of the database.

    Note! If there is no database, no backup is created.
    """

    backup_folder = paths.BACKUP_FOLDER

    if not backup_folder.exists():
        backup_folder.mkdir()

    if not paths.DATA_FOLDER_PATH.exists():
        return

    date = datetime.datetime.now().date().isoformat()

    if prefix is not None:
        prefix = prefix.replace("/", "")
        basename = prefix + date
    else:
        basename = date

    archive_path = backup_folder / basename
    counter = 0

    while Path(str(archive_path) + ".zip").exists():
        counter += 1
        archive_path = backup_folder / (basename + " " + str(counter))

    shutil.make_archive(str(archive_path), "zip", paths.DATA_FOLDER_PATH)

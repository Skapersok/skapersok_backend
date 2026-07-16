# Backup system

The backend can create full zip archives of the persisted data directory so the item database, user database, and image files can be restored later.

## Who can manage backups?

Backup management requires the admin role.

## What is backed up?

A backup includes the contents of the data directory, including:

- SQLite database files
- image files in the image folders
- other persisted runtime data under data/

Temporary or generated cache files are not treated as a separate backup artifact.

## Backup metadata

Each backup archive is identified by:

- a timestamp in the format YYYY-MM-DDTHH-MM-SS.ffffff
- a unique ID generated for the backup

The backup archives are stored in the data/backups directory.

## Backup routes

### GET /backups/get/all

Returns a list of backup objects with id, timestamp, and size.

### POST /backups/dump

Creates a new backup immediately from the current state of the data directory.

### POST /backups/schedule_restore

Schedules a restore from a specific backup ID. The restore is applied the next time the server starts.

### DELETE /backups/remove

Deletes a backup archive by ID.

## Notes

- The system also performs periodic backups based on the BACKUP_INTERVAL_SECONDS setting.
- The restore flow removes the current data directory and replaces it with the backup contents.
- If a restore is scheduled but the backup no longer exists, the restore is skipped and the pending state is written to config/pending_restore.failed.json.

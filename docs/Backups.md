# How the backup system works

Only admins can manage backups.

Each backups covers the database in its entirety, not including automatically generated cache files.

## Metadata

Each backup has the following metadata:
- Timestamp with second-resolution.
- An unique ID

## Routes

GET /backups/get/all
- Returns list of all backup names, 
  - name
  - id
  - size in bytes

POST /backups/dump
- Creates a backup from the current state of the item repository.

POST /backups/restore
- Arguments:
  - id: the id of the backup to restore from

DELETE /backups/remove
- Arguments:
  - id: the id the the backup to remove

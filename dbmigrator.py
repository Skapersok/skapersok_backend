import itemdbmigrator
import userdbmigrator

import backups


def migrate():
    """
    Updates the database to the latest version.
    This will create a backup before trying to migragte in case of faliure.
    """
    print("=== Database migration ===")
    print("Creating backup...")
    backups.create_backup()

    print("Migrating database...\n")
    itemdbmigrator.migrate()
    print("Migrating user database...\n")
    userdbmigrator.migrate()

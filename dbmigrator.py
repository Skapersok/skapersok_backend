import custom_values_dbmigrator
import itemdbmigrator
import userdbmigrator

import backups


def migrate():
    """
    Updates the database to the latest version.
    This will create a backup before trying to migragte in case of faliure.
    """
    all_up_to_date = itemdbmigrator.is_up_to_date() and userdbmigrator.is_up_to_date()
    if all_up_to_date:
        print("No database migration needed, the database is up to date.")
        return

    print("=== Database migration ===")
    print("Creating backup...")
    backups.dump()

    print("\nMigrating database...")
    itemdbmigrator.migrate()

    print("\nMigrating user database...")
    userdbmigrator.migrate()

    print("\nCustom values database migration...")
    custom_values_dbmigrator.migrate()

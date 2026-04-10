import getpass

import dbmigrator

import paths
import os
import shutil
import auth


# returns True if there is any data stored in the database, otherwise False
def some_database():
    if (
        paths.DATABASE_PATH.exists()
        or paths.USERBASE_PATH.exists()
        or (
            paths.MAP_IMAGE_FOLDER.exists()
            and not os.listdir(paths.MAP_IMAGE_FOLDER) == []
        )
        or (
            paths.DESCRIPTION_IMAGE_FOLDER.exists()
            and not os.listdir(paths.DESCRIPTION_IMAGE_FOLDER) == []
        )
    ):
        return True
    return False


# Returns False if n, True if yes
def user_confirms(prompt):
    prompt = prompt + " (y/n): "

    user_confirmed = False

    while not user_confirmed:
        response = input(prompt)

        if response.lower() == "n":
            return False
        elif response.lower() == "y":
            user_confirmed = True

    return True


def setup():
    if some_database():
        if user_confirms(
            "Some parts of the database exists. Delete it before creating a new?"
        ):
            shutil.rmtree(paths.DATA_FOLDER_PATH)
        else:
            return

    # Create files
    print("Creating databases...")
    dbmigrator.migrate()
    print("Databases created!")
    print()
    print("Time to create the first user!")
    username = input("Username: ")  # TODO: check username validity

    password_match = False
    while not password_match:
        password1 = getpass.getpass(prompt="Enter  the  password: ")
        password2 = getpass.getpass(prompt="Reenter the password: ")
        if password1 == password2:
            password_match = True
        else:
            print("Passwords must be equal.")
    password = password1

    auth.create_user(username, password, "admin")

    print("Created user", username)
    print("Setup successful!")


if __name__ == "__main__":
    setup()

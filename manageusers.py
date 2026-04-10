import getpass
import auth


if __name__ == "__main__":
    print("Create users...")
    username = input("Username: ")

    password_match = False
    while not password_match:
        password1 = getpass.getpass(prompt="Enter  the  password: ")
        password2 = getpass.getpass(prompt="Reenter the password: ")
        if password1 == password2:
            password_match = True
        else:
            print("Passwords must be equal.")
    password = password1

    while True:
        role = input("Role (admin/maintainer/editor/viewer): ")
        if role in auth.ROLES:
            break
        else:
            print(
                "Invalid role. Please enter one of: admin, maintainer, editor, viewer."
            )

    auth.create_user(username, password, role)

    print("Successfully created a new user with username", username)

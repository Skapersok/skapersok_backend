import getpass

import auth


def create_user():
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


if __name__ == "__main__":
    print("User management")
    try:
        while True:
            print("1. Create a new user")
            print("2. List all users")
            print("3. Delete a user")
            print("4. Exit")

            choice = input("Enter your choice: ")
            if choice == "1":
                create_user()
            elif choice == "2":
                users = auth.get_all_users()
                for user in users:
                    print(
                        f" - Username: {user.username}, Role: {user.role}, ID: {user.id}"
                    )
            elif choice == "3":
                users = auth.get_all_users()
                print("Existing users:")
                for user in users:
                    print(
                        f" - Username: {user.username}, Role: {user.role}, ID: {user.id}"
                    )
                username = input("Enter the username of the user to delete: ")
                auth.delete_user(username)
                print(f"Deleted user with username: {username}")
            elif choice == "4":
                print("Exiting.")
                break
            else:
                print("Invalid choice. Please enter a number between 1 and 3.")

    except KeyboardInterrupt:
        print("\nExiting.")

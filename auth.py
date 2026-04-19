from datetime import datetime, timedelta, timezone
from typing import Annotated, Any
from fastapi import Depends, status, HTTPException
from fastapi.security import OAuth2PasswordBearer
import jwt
import settings
from pwdlib import PasswordHash
from pydantic import BaseModel
import sqlite3
import paths


ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


class User(BaseModel):
    id: int
    username: str
    role: str


class UserInDB(User):
    hashed_password: str


password_hash = PasswordHash.recommended()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_all_users() -> list[User]:
    conn = sqlite3.connect(paths.USERBASE_PATH, timeout=30, check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, role FROM users")
    users = [User(id=row[0], username=row[1], role=row[2]) for row in cursor.fetchall()]
    conn.close()
    return users


def create_user(username: str, password: str, role: str):
    hashed_password = get_password_hash(password)
    conn = sqlite3.connect(paths.USERBASE_PATH, timeout=30, check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
        (username, hashed_password, role),
    )
    conn.commit()
    conn.close()


def user_exists(username: str) -> bool:
    conn = sqlite3.connect(paths.USERBASE_PATH, timeout=30, check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM users WHERE username=?", (username,))
    exists = cursor.fetchone() is not None
    conn.close()
    return exists


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_hash.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return password_hash.hash(password)


def get_user(username: str) -> UserInDB | None:
    conn = sqlite3.connect(paths.USERBASE_PATH, timeout=30, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username=?", (username,))
    row = cursor.fetchone()
    conn.close()

    if row is None:
        return None

    user_dict: dict[str, int | str | list[str]] = {
        "id": int(row["id"]),
        "username": row["username"],
        "hashed_password": row["password_hash"],
        "role": row["role"] if row["role"] else "viewer",
    }
    return UserInDB(**user_dict)


def authenticate_user(username: str, password: str):
    user = get_user(username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict[str, Any], expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET, algorithm=ALGORITHM)
    return encoded_jwt


def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
    )
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None or not isinstance(username, str):
            raise credentials_exception
        token_data = TokenData(username=username)
    except:
        raise credentials_exception
    user = get_user(str(token_data.username))
    if user is None:
        raise credentials_exception
    return user


def update_user_role(username: str, new_role: str):
    if new_role not in ROLES:
        raise ValueError(f"Invalid role: {new_role}")

    conn = sqlite3.connect(paths.USERBASE_PATH, timeout=30, check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET role=? WHERE username=?", (new_role, username))
    conn.commit()
    conn.close()


def update_user_password(username: str, new_password: str):
    hashed_password = get_password_hash(new_password)

    conn = sqlite3.connect(paths.USERBASE_PATH, timeout=30, check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE users SET password_hash=? WHERE username=?", (hashed_password, username)
    )
    conn.commit()
    conn.close()


def delete_user(username: str):
    conn = sqlite3.connect(paths.USERBASE_PATH, timeout=30, check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE username=?", (username,))
    conn.commit()
    conn.close()


def all_users() -> list[User]:
    conn = sqlite3.connect(paths.USERBASE_PATH, timeout=30, check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, role FROM users")
    users = [User(id=row[0], username=row[1], role=row[2]) for row in cursor.fetchall()]
    conn.close()
    return users


def get_all_users_with_role(role: str) -> list[User]:
    users = all_users()
    return [user for user in users if user.role == role]


def require_role(role: str | list[str]):
    async def role_dependency(
        current_user: Annotated[User, Depends(get_current_user)],
    ):
        if isinstance(role, list):
            if current_user.role not in role:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"User does not have any of the required roles: {role}",
                )
        else:
            if role != current_user.role:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"User does not have '{role}' role",
                )
        return current_user

    return role_dependency


# Admin: Can do everything
# Maintainer: Can do everything except user management
# Editor: Can edit items, but not manage users, delete or add items
# Viewer: Can only view items
ROLES = {"admin", "maintainer", "editor", "viewer"}

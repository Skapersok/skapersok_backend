import multiprocessing
from typing import Annotated
from fastapi.responses import FileResponse
from fastapi import Depends, FastAPI, File, Form, HTTPException, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from auth import (
    Token,
    authenticate_user,
    create_access_token,
    get_current_user,
    require_role,
    User,
)
import auth
import backups
from beacon import beacon
from settings import settings, ALLOWED_SETTINGS, list_settings, get_setting, set_setting
import database as db
from pydantic import BaseModel
from contextlib import asynccontextmanager
import dbmigrator
import custom_values
import constants

import sys
import os

def _supports_color():
    """Check if the terminal supports ANSI color codes."""

    if os.environ.get("NO_COLOR") is not None:
        return False

    if os.environ.get("FORCE_COLOR") is not None:
        return True

    if not hasattr(sys.stdout, "isatty") or not sys.stdout.isatty():
        return False
    
    if os.name == "nt":
        # Windows 10+ terminals support ANSI; older cmd.exe doesn't
        return "ANSICON" in os.environ or "WT_SESSION" in os.environ or "TERM" in os.environ

    return True


def print_startup_message():
    import art

    use_color = _supports_color()

    def colorize(text, code):
        return f"\033[{code}m{text}\033[0m" if use_color else text

    divider = "─" * 66
    skapersok = art.text2art("Skapersok", chr_ignore=True)
    skapersok = "\n".join(s.center(len(divider)) for s in skapersok.split("\n"))
    version_line = f"v{constants.version}".center(len(divider))

    print()
    print(colorize(divider, "2"))
    print(colorize(skapersok, "96"))   # cyan
    print(colorize(divider, "2"))      # dim
    print(colorize(version_line, "92"))  # green
    print(colorize(divider, "2"))      # dim
    print()
    print("Welcome to the Skapersøk backend!".center(len(divider)))
    print("For help, please visit: https://docs.skapersok.no/".center(len(divider)))
    print()
    print(colorize(divider, "2"))
    if not constants.in_docker and settings.autoopen_browser:
        print()
        print("A browser window should have opened. If not, please visit:".center(len(divider)))
        print(constants.local_server_url.center(len(divider)))
        print()
        print(colorize(divider, "2"))

    print()

@asynccontextmanager
async def lifespan(app: FastAPI):

    print_startup_message()
    backup_process = None

    # === Startup code ===

    # Apply scheduled restore before normal DB usage
    try:
        backups.apply_scheduled_restore()
    except Exception as e:
        print(f"Scheduled restore failed: {e}")

    dbmigrator.migrate()

    # Server ID
    server_id = settings.id
    server_name = db.get_root()["name"]

    # Start beacon once
    beacon.start(
        server_port=settings.port,
        server_name=server_name,
        server_id=server_id,
    )

    # Start backup process once
    backup_process = multiprocessing.Process(
        target=backups.periodic_backup,
        daemon=True,
        name="backuper",
    )
    backup_process.start()

    # === The server runs here ===
    try:
        yield
    finally:
        if backup_process is not None and backup_process.is_alive():
            backup_process.terminate()
            backup_process.join(timeout=5)

    # === Shutdown code goes here ===


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://app.skapersok.no",
        "https://www.skapersok.no",
    ],
    allow_origin_regex=r"^https?://(localhost|127\.0\.0\.1)(:\d+)?$",
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Accept", "Origin"],
)


class Item(BaseModel):
    placement_code: str
    name: str | None = None
    description: str | None = None
    keywords: str | None = None
    children_arrangement: str | None = None
    self_alignment: str | None = None


@app.get("/version")
async def get_version():
    return {"version": constants.version}


@app.post("/auth/login")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.username})

    return Token(access_token=access_token, token_type="bearer")


@app.get("/auth/authorized")
async def authorized(current_user: Annotated[User, Depends(get_current_user)]):
    return {"message": f"Hello {current_user.username}, you are authorized :)"}


@app.post("/users/create")
async def create_user(
    username: str = Form(...),
    password: str = Form(...),
    role: str = Form(...),
    user: User = Depends(require_role("admin")),
):
    if role not in auth.ROLES:
        raise HTTPException(status_code=400, detail="Invalid role.")

    try:
        auth.create_user(username, password, role)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {"status": "success"}


@app.put("/users/update")
async def update_user(
    username: str = Form(...),
    new_password: str | None = Form(None),
    new_role: str | None = Form(None),
    user: User = Depends(require_role("admin")),
):
    if new_role is not None and new_role not in auth.ROLES:
        raise HTTPException(status_code=400, detail="Invalid role.")

    try:
        if new_password is not None:
            auth.update_user_password(username, new_password)
        if new_role is not None:
            # Check if this is the last admin before changing the role
            all_admins = auth.get_all_users_with_role("admin")
            if (
                len(all_admins) == 1
                and all_admins[0].username == username
                and not new_role == "admin"
            ):
                raise HTTPException(
                    status_code=400,
                    detail="Cannot make the last admin user not an admin.",
                )
            auth.update_user_role(username, new_role)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {"status": "success"}


@app.delete("/users/remove")
async def remove_user(
    username: str = Form(...),
    user: User = Depends(require_role("admin")),
):

    all_admins = auth.get_all_users_with_role("admin")
    if len(all_admins) == 1 and all_admins[0].username == username:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete the last admin user. Create another admin before deleting this one.",
        )
    try:
        auth.delete_user(username)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {"status": "success"}


@app.get("/users/get/all")
async def get_all_users(user: User = Depends(require_role("admin"))):
    users = auth.all_users()

    return list(map(lambda user: {"username": user.username, "role": user.role}, users))


@app.get("/users/get/me")
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    user_raw = auth.get_user(current_user.username)
    user = User(id=user_raw.id, username=user_raw.username, role=user_raw.role)

    return {"username": user.username, "role": user.role, "id": user.id}


@app.get("/id")
async def get_server_id():
    return {"id": settings.id}


@app.get("/ping")
async def ping():
    return {"message": "pong"}


@app.get("/get/root")
async def get_root():
    placement_code = ""
    if not db.exists(placement_code):
        raise HTTPException(status_code=404, detail="Root not found.")

    item = db.get(placement_code)
    return item


@app.get("/get/all")
async def get_all(only_leaves: bool = False):
    all_items = db.get_all()
    if only_leaves:
        all_items = list(
            filter(lambda item: db.is_leaf(item["placement_code"]), all_items)
        )

    all_items.sort(key=lambda item: item["name"])
    return all_items


@app.get("/get/children/root")
async def get_children_root():
    placement_code = ""
    if not db.exists(placement_code):
        raise HTTPException(status_code=404, detail="Placement not found.")

    children = map(lambda code: db.get(code), db.get_children(placement_code))

    return list(children)


@app.get("/get/children")
async def get_children(code: str | None = ""):

    if not db.exists(code):
        raise HTTPException(status_code=404, detail="Placement not found.")

    children = map(lambda code: db.get(code), db.get_children(code))
    return list(children)


@app.get("/get")
async def get(code: str | None = ""):
    if not db.exists(code):
        raise HTTPException(status_code=404, detail="Placement not found.")

    item = db.get(code)
    return item


@app.get("/search")
async def search(
    q: str = "",
    max_results: int | None = None,
    skip_number: int = 0,
    only_leaves: bool = False,
    info_level: int = 1,
) -> dict[str, int | list[dict[str, str | bool | None]]]:
    """
    ## Query parameters
    info_level:

        - 0: all info

        - 1: only placement_code and name
    """

    if info_level not in (0, 1):
        raise HTTPException(status_code=100, detail="info_level must be one of 0 or 1")

    results = db.search(q, only_leaves, max_results, skip_number)

    if info_level == 0:
        results = (
            results[0],
            db.construct_multiple_full(results[1]),
        )
    elif info_level == 1:
        results = (
            results[0],
            db.construct_multiple(results[1], columns=["placement_code", "name"]),
        )
    response = {"total_matches": results[0], "results": results[1]}
    return response


@app.get("/trail")
async def trail(
    code: str = "",
) -> list[dict[str, None | bool | str | list[dict[str, str | None | bool]]]]:
    if not db.exists(code):
        raise HTTPException(status_code=404, detail="Placement not found.")

    locations_codes = code.split("-")

    layers = []

    for depth in range(len(locations_codes) - 1):
        layer = {}
        code = "-".join(locations_codes[: depth + 1])

        layer = db.get(code)

        layer["siblings"] = []
        siblings = db.get_siblings(code)

        for sibling in siblings:

            layer["siblings"].append(db.get(sibling["placement_code"]))

        layers.append(layer)

    return layers


@app.get("/has_children")
async def has_children(code: str = ""):
    if not db.exists(code):
        raise HTTPException(status_code=404, detail="Placement not found.")

    return {"has_children": not db.is_leaf(code)}


@app.get("/descimage/root")
async def descimage_root():
    """
    Sends the description image of the root
    """
    placement_code = ""
    if not db.exists(placement_code):
        raise HTTPException(status_code=404, detail="Placement not found.")

    path = db.description_image_path(placement_code)

    if not path.exists():
        raise HTTPException(status_code=404, detail="Description image not found.")

    return FileResponse(path)


@app.get("/mapimage/root")
async def mapimage_root():
    """
    Sends the map image of the root
    """
    placement_code = ""
    if not db.exists(placement_code):
        raise HTTPException(status_code=404, detail="Placement not found.")

    path = db.map_image_path(placement_code)

    if not path.exists():
        raise HTTPException(status_code=404, detail="Map image not found.")

    return FileResponse(path)


@app.get("/descimage")
async def descimage(code: str | None = ""):
    """
    Sends the description image
    """
    if not db.exists(code):
        raise HTTPException(status_code=404, detail="Placement not found.")

    path = db.description_image_path(code)

    if not path.exists():
        raise HTTPException(status_code=404, detail="Description image not found.")

    return FileResponse(path)


@app.get("/mapimage")
async def mapimage(code: str | None = ""):
    """
    Sends the map image
    """
    if not db.exists(code):
        raise HTTPException(status_code=404, detail="Placement not found.")

    path = db.map_image_path(code)

    if not path.exists():
        raise HTTPException(status_code=404, detail="Map image not found.")

    return FileResponse(path)


@app.post("/add")
async def add_item(
    placement_code: str = Form(...),
    name: str = Form(...),
    description: str | None = Form(None),
    keywords: str | None = Form(None),
    children_arrangement: str | None = Form(None),
    self_alignment: str | None = Form(None),
    map_image: UploadFile | None = File(None),
    desc_image: UploadFile | None = File(None),
    custom_values: dict[str, str] | None = Form(None),
    user: User = Depends(require_role(["admin", "maintainer"])),
):
    if db.exists(placement_code):
        raise HTTPException(status_code=400, detail="Placement code already exists.")

    if not db.verify_placement_code_syntax(placement_code):
        raise HTTPException(status_code=400, detail="Invalid placement code syntax.")

    if db.get_parent_code(placement_code) is None or not db.exists(
        db.get_parent_code(placement_code)
    ):
        raise HTTPException(
            status_code=400, detail="Parent placement code does not exist."
        )

    db.add(
        placement_code=placement_code,
        name=name,
        description=description,
        keywords=keywords,
        children_arrangement=children_arrangement,
        self_alignment=self_alignment,
        custom_values=custom_values,
    )

    if map_image is not None:
        path = db.map_image_path(placement_code)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(await map_image.read())

    if desc_image is not None:
        path = db.description_image_path(placement_code)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(await desc_image.read())

    return {"status": "success"}


@app.delete("/remove")
async def remove_item(
    codes: list[str] = Form(...),
    user: User = Depends(require_role(["admin", "maintainer"])),
):
    if not db.all_exists(codes):
        raise HTTPException(status_code=404, detail="One or more items not found.")

    db.remove(codes)
    return {"status": "success"}


@app.put("/update/root")
async def update_root(
    name: str | None = Form(None),
    description: str | None = Form(None),
    keywords: str | None = Form(None),
    children_arrangement: str | None = Form(None),
    self_alignment: str | None = Form(None),
    map_image: UploadFile | None = None,
    desc_image: UploadFile | None = None,
    custom_values: dict[str, str] | None = Form(None),
    user: User = Depends(require_role(["admin", "maintainer", "editor"])),
):
    placement_code = ""

    if not db.exists(placement_code):
        raise HTTPException(status_code=404, detail="Placement not found.")

    db.update(
        placement_code,
        name=name,
        description=description,
        keywords=keywords,
        children_arrangement=children_arrangement,
        self_alignment=self_alignment,
        custom_values=custom_values,
    )

    if map_image is not None:
        # db.set_map_image(placement_code, map_image)
        path = db.map_image_path(placement_code)
        if path.exists():
            path.unlink()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(await map_image.read())

    if desc_image is not None:
        # db.set_description_image(placement_code, desc_image)
        path = db.description_image_path(placement_code)
        if path.exists():
            path.unlink()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(await desc_image.read())

    return {"status": "success"}


@app.put("/update")
async def update_item(
    code: str,
    new_placement_code: str | None = Form(None),
    name: str | None = Form(None),
    description: str | None = Form(None),
    keywords: str | None = Form(None),
    children_arrangement: str | None = Form(None),
    self_alignment: str | None = Form(None),
    custom_values: dict[str, str] | None = Form(None),
    map_image: UploadFile | None = None,
    desc_image: UploadFile | None = None,
    user: User = Depends(require_role(["admin", "maintainer", "editor"])),
):
    if not db.exists(code):
        raise HTTPException(status_code=404, detail="Placement not found.")

    db.update(
        code,
        name=name,
        description=description,
        keywords=keywords,
        children_arrangement=children_arrangement,
        self_alignment=self_alignment,
        custom_values=custom_values,
    )

    if new_placement_code is not None and new_placement_code != code:
        db.update_placement_code(code, new_placement_code)

    if map_image is not None:
        await db.set_map_image(code, map_image)

    if desc_image is not None:
        await db.set_description_image(code, desc_image)

    return {"status": "success"}


# === Backups ===


@app.get("/backups/get/all")
async def get_all_backups(user: User = Depends(require_role("admin"))):
    """
    Returns a list of all available backups.
    """

    return [
        {"id": b.id, "timestamp": b.timestamp, "size": b.size}
        for b in backups.all_backups()
    ]


@app.post("/backups/dump")
async def dump_backup(user: User = Depends(require_role("admin"))):
    """
    Creates a backup of the database in its current state.
    """

    backups.dump()


@app.post("/backups/schedule_restore")
async def schedule_backup_restore(id: str, user: User = Depends(require_role("admin"))):
    """
    Schedules a restore from the backup id requested. The changes will be applied next startup.
    """

    info = backups.BackupInfo.from_id(id)
    if info is None:
        raise HTTPException(status_code=404, detail="Backup not found.")

    backups.dump()
    backups.schedule_restore(info, requested_by=user.username)

    return {
        "status": "scheduled",
        "message": "Restore scheduled. Restart the server to apply it.",
        "backup_id": id,
    }


@app.delete("/backups/remove")
async def remove_backup(id: str, user: User = Depends(require_role("admin"))):
    """
    Removes the specified backup.
    """

    info = backups.BackupInfo.from_id(id)
    if info is None:
        raise HTTPException(status_code=404, detail="Backup not found.")

    backups.remove_backup(info)


@app.get("/settings/get")
async def settings_get(id: str):
    if not id in ALLOWED_SETTINGS:
        raise HTTPException(
            401,
            "Setting must be one of: " + ", ".join(ALLOWED_SETTINGS.keys()),
        )
    return get_setting(id)


class SettingsPayload(BaseModel):
    image_quality: int | None = None
    max_backups_size: int | None = None
    backup_interval_seconds: int | None = None


class SettingsUpdate(BaseModel):
    settings: SettingsPayload


@app.put("/settings/update")
async def update_settings(
    body: SettingsUpdate,
    user: User = Depends(require_role("admin")),
):
    updates = body.settings.model_dump(exclude_none=True)

    # Validate all settings
    all_settings = list_settings()
    for name in updates:
        if name not in all_settings:
            raise HTTPException(status_code=400, detail=f"Unknown setting: {name}")

    for name, value in updates.items():
        set_setting(name, value)

    return {"status": "success"}


@app.get("/custom_value_types/get/<id>")
async def get_custom_value_type(id: str):
    value_type = custom_values.get_type(id)

    if value_type is None:
        raise HTTPException(status_code=404, detail="Custom value type not found.")

    return value_type


@app.get("/custom_value_types/get/all")
async def get_all_custom_value_types():
    return custom_values.get_all_types()

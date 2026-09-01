import os
import urllib.parse
import webbrowser
import time

from settings import settings

import importlib.metadata
import tomllib
from pathlib import Path


def get_version() -> str:
    try:
        with Path(__file__).resolve().parent.joinpath("pyproject.toml").open("rb") as f:
            return tomllib.load(f)["project"]["version"]
    except Exception:
        try:
            return importlib.metadata.version("skapersok_backend")
        except importlib.metadata.PackageNotFoundError:
            return "unknown"

version = get_version()


in_docker = os.environ.get("RUNNING_IN_DOCKER") == "true"

# Returns the local IP address of the machine, or None if it cannot be determined.
def local_ip() -> str | None:
    import socket

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    except OSError:
        return None  # e.g. no network available
    finally:
        s.close()


def _get_local_server_url():
    local_ip_address = local_ip()
    if not local_ip_address:
        return None

    server_url = f"http://{local_ip_address}:{settings.port}"

    encoded_url = "https://skapersok.no/join?url=" + urllib.parse.quote(
        server_url, safe=""
    )
    return encoded_url

local_server_url = _get_local_server_url()
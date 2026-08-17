import os
import threading
import time

import uvicorn

import paths
import routing
from settings import ensure_env_defaults, settings

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

def _open_browser():
    # Start browser if applicable
    if not settings.autoopen_browser:
        return

    time.sleep(1)  # give uvicorn a moment to bind the port

    import urllib.parse
    import webbrowser

    local_ip_address = local_ip()
    if not local_ip_address:
        # Not online, reaching skapersok.no will not work
        return
    server_url = f"http://{local_ip_address}:{settings.port}"

    encoded_url = "https://skapersok.no/join?url=" + urllib.parse.quote(
        server_url, safe=""
    )
    webbrowser.open(encoded_url)


def main():
    paths.ensure_exists()
    ensure_env_defaults()

    # never try to open a browser inside a container - there isn't one
    in_docker = os.environ.get("RUNNING_IN_DOCKER") == "true"
    if settings.autoopen_browser and not in_docker:
        threading.Thread(target=_open_browser, daemon=True).start()

    uvicorn.run(routing.app, host="0.0.0.0", port=settings.port)


if __name__ == "__main__":
    main()
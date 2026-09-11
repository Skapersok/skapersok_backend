import multiprocessing
import os
import threading
import time

import uvicorn

import constants
import paths
import routing
from settings import ensure_env_defaults, settings


def _open_browser() -> None:
    # Start browser if applicable
    if not settings.autoopen_browser:
        return

    time.sleep(1)  # give uvicorn a moment to bind the port

    import webbrowser

    encoded_url = constants.local_server_url
    if not encoded_url:
        return

    webbrowser.open(encoded_url)


def main() -> None:
    paths.ensure_exists()
    ensure_env_defaults()

    # never try to open a browser inside a container - there isn't one
    in_docker = os.environ.get("RUNNING_IN_DOCKER") == "true"
    if settings.autoopen_browser and not in_docker:
        threading.Thread(target=_open_browser, daemon=True).start()

    uvicorn.run(routing.app, host="0.0.0.0", port=settings.port)


if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()

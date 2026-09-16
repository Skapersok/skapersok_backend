import json
import multiprocessing
import socket

BEACON_PORT = 50000
CLIENT_REQUEST_IDENTIFIER = "WHERE_IS_SERVER"
BEACON_RESPONSE_PREFIX = "SERVER_IS:"


_config_queue = None
_stop_event = None


def start(server_port: int, server_name: str, server_id: str, stop_event: multiprocessing.Event):
    global _config_queue
    global _stop_event

    _config_queue = multiprocessing.Queue()
    _stop_event = stop_event

    # Send initial config
    _config_queue.put(
        {
            "port": server_port,
            "name": server_name,
            "id": server_id,
        }
    )

    process = multiprocessing.Process(
        target=_run,
        args=(_config_queue,),
        daemon=True,
        name="beacon",
    )

    process.start()


def update_config(
    server_port: int | None = None,
    server_name: str | None = None,
    server_id: str | None = None,
):
    """Update beacon configuration in real-time"""
    global _config_queue
    if _config_queue is not None:
        _config_queue.put(
            {
                "port": server_port,
                "name": server_name,
                "id": server_id,
            }
        )


def _run(config_queue):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.settimeout(1.0)  # Add 1 second timeout
    sock.bind(("", BEACON_PORT))

    # Initial config from queue
    info = config_queue.get()
    try:
        while not _stop_event.is_set():
            # Check for config updates (non-blocking)
            try:
                new_info = config_queue.get_nowait()
                if new_info["name"] is not None:
                    info["name"] = new_info["name"]
                if new_info["port"] is not None:
                    info["port"] = new_info["port"]
                if new_info["id"] is not None:
                    info["id"] = new_info["id"]

            except:
                pass  # No new config, use existing

            response = f"{BEACON_RESPONSE_PREFIX}" + json.dumps(info)
            try:
                data, addr = sock.recvfrom(1024)

                if not data.decode() == CLIENT_REQUEST_IDENTIFIER:
                    # Ignore those who does not know how to ask
                    continue

                sock.sendto(response.encode(), addr)  # unicast reply
            except TimeoutError:
                pass  # Timeout allows loop to check for interrupts
    finally:
        print("Beacon stopped.")
        sock.close()

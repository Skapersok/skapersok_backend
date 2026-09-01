import socket
import json
import multiprocessing

BEACON_PORT = 50000
CLIENT_REQUEST_IDENTIFIER = "WHERE_IS_SERVER"
BEACON_RESPONSE_PREFIX = "SERVER_IS:"


_config_queue = None


def start(server_port: int, server_name: str, server_id: str):
    global _config_queue

    _config_queue = multiprocessing.Queue()

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
        while True:

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
            except socket.timeout:
                pass  # Timeout allows loop to check for interrupts
    except KeyboardInterrupt:
        # Graceful exit on Ctrl+C
        print("Beacon stopped.")
    finally:
        sock.close()


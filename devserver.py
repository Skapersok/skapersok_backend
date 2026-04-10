import uvicorn

if __name__ == "__main__":

    server_config = uvicorn.Config(
        "main:app", host="0.0.0.0", port=5000, log_level="info", reload=True
    )
    server = uvicorn.Server(server_config)
    try:
        server.run()
    except KeyboardInterrupt:
        print("Server stopped by user.")

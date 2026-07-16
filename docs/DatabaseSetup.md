# Database setup

The backend uses a small number of configuration values stored in config/.env.

## Required variables

### JWT_SECRET

A strong secret used to sign authentication tokens.

Example:

```dotenv
JWT_SECRET=replace-this-with-a-long-random-secret
```

## Optional variables

### ACCESS_TOKEN_EXPIRE_MINUTES

How long access tokens stay valid. Default is 60.

### IMAGE_QUALITY

Image quality used by the image processing pipeline. Default is 85.

### MAX_BACKUPS_SIZE

Maximum total size of backup archives in bytes. Default is 1000000000.

### BACKUP_INTERVAL_SECONDS

How often periodic backups run. Default is 3600 seconds.

### ID

A UUID used as the server identifier. If not set, the application generates one automatically.

## Setup flow

1. Create a virtual environment and install dependencies.
2. Create config/.env and set JWT_SECRET.
3. Run python3 setup.py to initialize the databases and create the first admin user.
4. Start the server with ./start.sh.

The application will create the required directories automatically when it starts.

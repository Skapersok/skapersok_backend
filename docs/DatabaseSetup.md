# In the .env

### Required Environment Variables

- **JWT_SECRET** = eg. your_jwt_secret_key

The jwt secret key is essential for securing authentication tokens in your application. Make sure to set a strong and unique value for this variable. **Do not share this key publicly.**

### Optional Environment Variables

- **SERVER_NAME** = eg. your_server_name (default: 'Unamed Server')
- **SERVER_PORT** = eg. 5000 (default: 5000)
- **BACKUP_FOLDER** = eg. relative_path_to_your_backup_folder (default: 'backups')
- **BACKUP_INTERVAL_SECONDS** = eg. 86400 (default: 86400 seconds = 24 hours)
- **ID** = a UUID v4. If not set, one will be generated automatically.

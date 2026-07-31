#!/bin/bash
set -e

# Fix ownership of bind-mounted volumes — these are mounted at runtime
# and may belong to root (or the host user) rather than appuser
chown -R appuser:appuser /app/data /app/config

# Drop from root to appuser to actually run the app
exec gosu appuser "$@"
#!/bin/bash
set -e

# Generate init.sql with the database name from the environment variable
echo "CREATE DATABASE IF NOT EXISTS \`${DB_NAME}\`;" > /docker-entrypoint-initdb.d/init.sql

# Execute the original entrypoint script
exec /usr/local/bin/docker-entrypoint.sh "$@"
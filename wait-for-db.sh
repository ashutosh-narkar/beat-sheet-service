#!/bin/sh

echo "Waiting for the database to start..."
while ! nc -z db 3306; do
  sleep 1
done

echo "Database started, running the application..."
exec "$@"


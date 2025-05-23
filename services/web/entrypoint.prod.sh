#!/bin/sh
if [ "$DATABASE" = "postgres" ]; 
then
    echo "Waiting for postgres..."

    while ! nc -z $SQL_HOST $SQL_PORT; do
      sleep 0.1
    done

    echo "PostgreSQL started"
fi

if [ "$FLASK_DEBUG" = "true" ]; 
then
    echo "Running in debug mode"
    echo "Creating database tables..."
    python manage.py create_db
    echo "Database tables created"
fi


exec "$@"
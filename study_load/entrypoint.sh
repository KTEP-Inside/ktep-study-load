#!/bin/sh
if [ "$DATABASE" = "mariadb" ]
then
  echo "Waiting for mariadb..."

  while ! nc -z $DB_HOST $DB_PORT; do
    sleep 0.1
  done

  echo "MySql started"
fi

#python manage.py flush --no-input
#python manage.py migrate
#python manage.py loaddata course.json exam.json semester.json typeload.json

exec "$@"
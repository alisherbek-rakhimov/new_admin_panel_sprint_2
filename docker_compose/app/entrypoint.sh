#!/bin/sh

set -e

cd /opt/app


python manage.py collectstatic --no-input --clear
python manage.py wait_for_db
python manage.py migrate


echo "$@"
exec $@

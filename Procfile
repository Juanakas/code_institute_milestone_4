release: python manage.py migrate && python manage.py collectstatic --noinput
web: gunicorn --no-sendfile bachata_club.wsgi
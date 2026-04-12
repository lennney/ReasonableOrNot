release: python manage.py migrate && python manage.py collectstatic --noinput
web: gunicorn login.wsgi --access-logfile - --error-logfile -

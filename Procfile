release: python manage.py migrate && python manage.py import_phones && python manage.py collectstatic --noinput
web: gunicorn login.wsgi --access-logfile - --error-logfile -

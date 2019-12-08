release: python wye_server_django/manage.py migrate -v3 && python wye_server_django/manage.py collectstatic --noinput
web: gunicorn wye_server_django.core.wsgi DJANGO_SETTINGS_MODULE=wye_server_django.core.settings --pythonpath wye_server_django

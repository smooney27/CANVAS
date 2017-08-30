import os, sys

import django.core.handlers.wsgi

os.environ['DJANGO_SETTINGS_MODULE'] = 'settings-webfaction-dove'
application = django.core.handlers.wsgi.WSGIHandler()

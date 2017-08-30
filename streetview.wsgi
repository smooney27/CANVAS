import os, sys
sys.path.append('/usr/lib/python2.6/site-packages/django')
sys.path.append('/var/www/vhosts/canvasplatform.org/httpdocs')
streetview_path = '/var/www/vhosts/canvasplatform.org/httpdocs/streetview'
if streetview_path not in sys.path:
    sys.path.append(streetview_path)
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings-canvasplatform'

import django.core.handlers.wsgi

application = django.core.handlers.wsgi.WSGIHandler()


"""
WSGI config for djapi project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/2.0/howto/deployment/wsgi/
"""

import os
import sys

from django.core.wsgi import get_wsgi_application

sys.path.append('/var/www/dodrian.com/djapi')

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "djapi.settings")

application = get_wsgi_application()

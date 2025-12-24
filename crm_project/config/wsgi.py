"""
WSGI config for CRM project.

This module contains the WSGI application used by Django's runserver
and other WSGI-compliant web servers. It exposes the WSGI callable as a
module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/stable/howto/deployment/wsgi/
"""

import os
from django.core.wsgi import get_wsgi_application  # type: ignore

# Set default settings module for 'wsgi' command-line argument
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

application = get_wsgi_application()
"""
ASGI config for CRM project.

This module contains the ASGI application used for deploying the project
on ASGI-compliant servers. It exposes the ASGI callable as a module-
level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/stable/howto/deployment/asgi/
"""

import os
from django.core.asgi import get_asgi_application  # type: ignore

# Set default settings module for 'asgi' command-line argument
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

application = get_asgi_application()
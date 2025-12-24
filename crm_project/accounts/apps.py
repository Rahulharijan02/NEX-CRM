"""
App configuration for the accounts application.

The Accounts app houses the custom User model and authentication
utilities. It is configured to use email addresses as usernames and
integrates with Django's authentication system.
"""

from django.apps import AppConfig


class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounts'
    verbose_name = 'Accounts'
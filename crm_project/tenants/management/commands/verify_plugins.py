"""Verify that key third-party packages ("plugins") are installed and wired.

Run:
  python manage.py verify_plugins

This command performs safe checks:
  - Imports DRF, SimpleJWT, drf-spectacular, django-filter
  - Prints versions
  - Confirms key URL names can be reversed
  - Confirms REST_FRAMEWORK filter backends include Search/Filter/Ordering
  - Tries to generate the OpenAPI schema (this catches filter mistakes)
"""

from django.conf import settings
from django.core.management.base import BaseCommand
from django.urls import reverse

from django.test.client import RequestFactory
from django.contrib.auth.models import AnonymousUser

from drf_spectacular.generators import SchemaGenerator


def _status_ok(status_code: int) -> bool:
    return status_code in (200, 201, 204)


class Command(BaseCommand):
    help = "Verify that DRF, SimpleJWT, drf-spectacular, and django-filter are installed and configured."

    def handle(self, *args, **options):
        import django
        # Imports
        import rest_framework  # noqa: F401
        import rest_framework_simplejwt  # noqa: F401
        import drf_spectacular  # noqa: F401
        import django_filters  # noqa: F401

        # Versions
        self.stdout.write(self.style.SUCCESS("Imports: OK"))
        self.stdout.write(f"Django: {django.get_version()}")
        self.stdout.write(f"DRF: {getattr(rest_framework, '__version__', 'unknown')}")
        self.stdout.write(f"SimpleJWT: {getattr(rest_framework_simplejwt, '__version__', 'unknown')}")
        self.stdout.write(f"drf-spectacular: {getattr(drf_spectacular, '__version__', 'unknown')}")
        self.stdout.write(f"django-filter: {getattr(django_filters, '__version__', 'unknown')}")

        # URL reversing
        url_names = [
            'home',
            'login',
            'logout',
            'register',
            'token_obtain_pair',
            'token_refresh',
            'token_verify',
            'schema',
            'swagger-ui',
        ]
        self.stdout.write("\nURL reverse checks:")
        for name in url_names:
            try:
                self.stdout.write(f"  {name}: {reverse(name)}")
            except Exception as exc:  # pragma: no cover
                self.stdout.write(self.style.ERROR(f"  {name}: FAILED ({exc})"))

        # DRF filter backends
        backends = settings.REST_FRAMEWORK.get('DEFAULT_FILTER_BACKENDS', [])
        self.stdout.write("\nDRF filter backends:")
        for b in backends:
            self.stdout.write(f"  - {b}")

        required = {
            'rest_framework.filters.SearchFilter',
            'django_filters.rest_framework.DjangoFilterBackend',
            'rest_framework.filters.OrderingFilter',
        }
        missing = required.difference(set(backends))
        if missing:
            self.stdout.write(self.style.WARNING(f"Missing backends: {sorted(missing)}"))
        else:
            self.stdout.write(self.style.SUCCESS("All expected backends are configured."))

        self.stdout.write(self.style.SUCCESS("\nVerification complete."))

        # Schema generation (catches django-filter / spectacular issues)
        self.stdout.write("\nOpenAPI schema generation:")
        try:
            rf = RequestFactory()
            request = rf.get('/api/schema/')
            # During schema generation in management commands, the request does not
            # pass through Django's authentication middleware, so `request.user`
            # is not automatically attached. drf-spectacular may call view
            # methods that expect `request.user` to exist.
            request.user = AnonymousUser()  # type: ignore[attr-defined]
            schema = SchemaGenerator().get_schema(request=request, public=True)
            path_count = len(schema.get('paths', {})) if isinstance(schema, dict) else 0

            # Check Swagger "Authorize" scheme exists in schema
            schemes = None
            if isinstance(schema, dict):
                schemes = (
                    schema.get('components', {})
                    .get('securitySchemes', {})
                )

            if not schemes or 'bearerAuth' not in schemes:
                self.stdout.write(self.style.WARNING("  Schema generated, but bearerAuth security scheme is missing."))
            else:
                self.stdout.write(self.style.SUCCESS("  bearerAuth security scheme found (Swagger Authorize should work)."))

            self.stdout.write(self.style.SUCCESS(f"  Schema generated OK. Paths: {path_count}"))
        except Exception as exc:
            self.stdout.write(self.style.ERROR(f"  Schema generation FAILED: {exc}"))

        # Quick auth check for APIs
        self.stdout.write("\nAPI auth checks:")
        try:
            from rest_framework.test import APIRequestFactory
            from crm.views import ContactViewSet

            api_rf = APIRequestFactory()

            # 1) No token -> should NOT be success
            view = ContactViewSet.as_view({'get': 'list'})
            req1 = api_rf.get('/api/contacts/')
            req1.user = AnonymousUser()  # type: ignore[attr-defined]
            resp1 = view(req1)
            if _status_ok(resp1.status_code):
                self.stdout.write(self.style.ERROR(f"  Contacts without token: UNEXPECTED {resp1.status_code}"))
            else:
                self.stdout.write(self.style.SUCCESS(f"  Contacts without token: OK ({resp1.status_code})"))

            # 2) Bad token -> should be 401/403
            req2 = api_rf.get('/api/contacts/', HTTP_AUTHORIZATION='Bearer not_a_real_token')
            req2.user = AnonymousUser()  # type: ignore[attr-defined]
            resp2 = view(req2)
            if _status_ok(resp2.status_code):
                self.stdout.write(self.style.ERROR(f"  Contacts with bad token: UNEXPECTED {resp2.status_code}"))
            else:
                self.stdout.write(self.style.SUCCESS(f"  Contacts with bad token: OK ({resp2.status_code})"))
        except Exception as exc:
            self.stdout.write(self.style.ERROR(f"  API auth checks FAILED: {exc}"))

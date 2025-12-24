"""Project URLs (simple)."""

from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path
from rest_framework.routers import SimpleRouter
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView

# Import API viewsets from our apps
from accounts.views import UserViewSet, AuthView, register
from crm.views import ContactViewSet, DealViewSet, ActivityViewSet
from clinic.views import PatientViewSet, AppointmentViewSet
from realestate.views import PropertyViewSet, ViewingViewSet
from .views import home, dashboard


router = SimpleRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'contacts', ContactViewSet, basename='contact')
router.register(r'deals', DealViewSet, basename='deal')
router.register(r'activities', ActivityViewSet, basename='activity')
router.register(r'patients', PatientViewSet, basename='patient')
router.register(r'appointments', AppointmentViewSet, basename='appointment')
router.register(r'properties', PropertyViewSet, basename='property')
router.register(r'viewings', ViewingViewSet, basename='viewing')

urlpatterns = [
    # Friendly landing page
    path('', home, name='home'),
    path('dashboard/', dashboard, name='dashboard'),

    path('admin/', admin.site.urls),
    # API endpoints
    # JWT auth
    path('api/auth/', AuthView.as_view(), name='token_obtain_pair'),
    path('api/auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/auth/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('api/', include(router.urls)),
    # API schema and docs
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    # Auth HTML views
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('register/', register, name='register'),
    # HTML pages provided by each app
    path('', include('crm.urls', namespace='crm')),
    path('', include('clinic.urls', namespace='clinic')),
    path('', include('realestate.urls', namespace='realestate')),
]
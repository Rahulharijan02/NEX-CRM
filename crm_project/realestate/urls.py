from django.urls import path

from . import views

app_name = 'realestate'

urlpatterns = [
    path('properties/', views.property_list, name='properties'),
    path('properties/create/', views.property_create, name='property_create'),
    path('viewings/', views.viewing_list, name='viewings'),
    path('viewings/create/', views.viewing_create, name='viewing_create'),
]

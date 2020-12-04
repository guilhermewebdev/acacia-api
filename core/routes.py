from rest_framework import routers
from . import views
from django.urls import path, include

core = routers.DefaultRouter()

core.register(r'professionals', views.Professionals, basename='Professional')
core.register(r'users', views.Users, basename='User')

professional = routers.DefaultRouter()
professional.register(r'availabilities', views.Availabilities, basename='Availability')

user = routers.DefaultRouter()
user.register(r'availabilities', views.PrivateAvailabilities, basename='Availability')

urls = [
    path('', include(core.urls)),
    path('professionals/<professional_uuid>/', include(professional.urls)),
    path('users/profile/', include(user.urls)),
]
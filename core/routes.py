from rest_framework import routers
from . import views
from django.urls import path, include

router = routers.DefaultRouter()

router.register(r'professionals', views.Professionals, basename='Professional')
router.register(r'users', views.Users, basename='User')

professional = routers.DefaultRouter()
professional.register(r'availabilities', views.Availabilities, basename='Availability')

user = routers.DefaultRouter()
user.register(r'availabilities', views.PrivateAvailabilities, basename='Availability')

urls = [
    path('', include(router.urls)),
    path('professionals/<professional_uuid>/', include(professional.urls)),
    path('users/profile/', include(user.urls)),
]
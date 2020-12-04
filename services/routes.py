from django.urls.conf import include, path
from rest_framework.routers import DefaultRouter
from . import views

services = DefaultRouter()
services.register(r'proposals', views.ProposalsViewset, basename='Proposal')

url = [
    path('', include(services.urls))
]

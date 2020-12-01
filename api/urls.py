"""api URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path, include
from financial.views import payment_postback
from core.views import professional_postback
from django.conf.urls.static import static
from django.conf import settings
from core.routes import router as core

urlpatterns = [
    path('', include(core.urls)),
    path('api-auth/', include('rest_framework.urls')),
    path('postback/payment/<uuid:str>/', payment_postback),
    path('postback/professional/<uuid:str>/', professional_postback),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

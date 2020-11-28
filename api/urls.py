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
from django.urls import path
from financial.views import payment_postback
from core.views import professional_postback
from graphene_django.views import GraphQLView
from django.views.decorators.csrf import csrf_exempt
from graphql_jwt.decorators import jwt_cookie
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('postback/payment/<uuid:str>/', payment_postback),
    path('postback/professional/<uuid:str>/', professional_postback),
    path('', jwt_cookie(csrf_exempt(GraphQLView.as_view(graphiql=settings.DEBUG))), name='GraphQL API'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

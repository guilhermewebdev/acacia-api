from django.urls.conf import path
from . import views

urls = [
    path('professionals/', views.ProfessionalList.as_view()),
    path('postback/professional/<uuid:str>/', views.professional_postback),
]
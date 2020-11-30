from api.utils import JSONList, JSONMixin
from django.http.response import JsonResponse
from django.shortcuts import render
from django.views.generic.list import ListView
from django.views.generic.base import View
from django.views.generic.edit import FormMixin
from . import models

def professional_postback(request, uuid):
    pass

class ProfessionalList(JSONMixin, JSONList, ListView):
    model = models.Professional

    @property
    def paginated_by(self):
        return int(self.request.GET.get('limit', 10))

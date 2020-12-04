from django.db.models.query_utils import Q
from . import models
from django.shortcuts import render
from rest_framework.viewsets import ViewSet, ModelViewSet

class ProposalsViewset(ModelViewSet):
    
    def get_queryset(self):
        if self.request.user.is_professional:
            return models.Proposal.objects.filter(
                Q(client=self.request.user) |
                Q(professional=self.request.user.professional)
            ).all()
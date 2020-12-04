from django.db.models.query_utils import Q
from rest_framework.decorators import action, permission_classes
from rest_framework.response import Response
from . import models, serializers
from django.shortcuts import render
from rest_framework.viewsets import ViewSet, ModelViewSet
from rest_framework.permissions import IsAuthenticated
from core.views import IsProfessional

class ProposalsViewset(ModelViewSet):
    serializer_class = serializers.ProposalSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'uuid'

    @property    
    def queryset(self):
        if self.request.user.is_professional:
            return models.Proposal.objects.filter(
                Q(client=self.request.user) |
                Q(professional=self.request.user.professional)
            ).all()
        return self.request.user.proposals.all()

    @action(methods=['get'], detail=False)
    def sent(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            self.queryset.filter(client=request.user),
            many=True,
            context={'request': request}
        )
        return Response(serializer.data)
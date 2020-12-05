from django.db.models.query_utils import Q
from rest_framework.decorators import action, permission_classes
from rest_framework.response import Response
from . import models, serializers
from django.shortcuts import get_object_or_404, render
from rest_framework.viewsets import ViewSet, ModelViewSet
from rest_framework.permissions import IsAuthenticated
from core.views import IsProfessional
from django.utils.translation import gettext as _

class ProposalsViewset(ViewSet):
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

    @action(methods=['put'], detail=True)
    def accept(self, request, uuid=None, *args, **kwargs):
        proposal: models.Proposal = get_object_or_404(self.queryset, uuid=uuid)
        if request.user == proposal.professional.user:
            proposal.accept()
            serializer = self.serializer_class(
                proposal,
                context={'request': request}
            )
            return Response(serializer.data)
        return Response({'error': _('Unauthorized')}, status=403)

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            data=request.data,
            context={'request': request},
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    def update(self, request, uuid=None, *args, **kwargs):
        proposal: models.Proposal = get_object_or_404(self.queryset, uuid=uuid)
        serializer = self.serializer_class(
            data=request.data,
            context={'request': request},
            instance=proposal,
        )
        if serializer.is_valid() and request.user == proposal.client:
            serializer.update(proposal, serializer.validated_data)
            proposal.full_clean()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    def retrieve(self, request, uuid=None, *args, **kwargs):
        proposal: models.Proposal = get_object_or_404(self.queryset, uuid=uuid)
        serializer = self.serializer_class(
            instance=proposal,
            context={'request': request},
        )
        return Response(data=serializer.data)

    def list(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            self.queryset,
            context={'request': request},
            many=True
        )
        return Response(serializer.data)

    @action(methods=['get'], detail=False, permission_classes=[IsProfessional])
    def received(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            self.queryset.filter(professional=request.user.professional),
            many=True,
            context={'request': request}
        )
        return Response(serializer.data)
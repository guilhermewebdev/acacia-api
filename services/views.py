from django.db.models.query_utils import Q
from django.http import request
from rest_framework.decorators import action, permission_classes
from rest_framework.response import Response
from . import models, serializers
from django.shortcuts import get_object_or_404
from rest_framework.viewsets import ViewSet
from rest_framework.permissions import IsAuthenticated
from core.views import IsProfessional
from django.utils.translation import gettext as _

class ProposalsViewSet(ViewSet):
    serializer_class = serializers.ProposalSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'uuid'

    @property    
    def queryset(self):
        return models.Proposal.objects.filter(
            Q(client=self.request.user) |
            Q(professional__user=self.request.user)
        ).all()

    @property
    def object(self):
        return get_object_or_404(
            self.queryset,
            uuid=self.kwargs.get('uuid')
        )

    @action(methods=['get'], detail=False)
    def sent(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            self.queryset.filter(client=request.user),
            many=True,
            context={'request': request}
        )
        return Response(serializer.data)

    def __accept_or_reject(self, request, uuid, accept):
        proposal: models.Proposal = get_object_or_404(self.queryset, uuid=uuid)
        if request.user == proposal.professional.user:
            proposal.accept() if accept else proposal.reject()
            serializer = self.serializer_class(
                proposal,
                context={'request': request}
            )
            return Response(serializer.data)
        return Response({'error': _('Unauthorized')}, status=403)

    @action(methods=['put'], detail=True)
    def accept(self, request, uuid=None, *args, **kwargs):
        return self.__accept_or_reject(request, uuid, True)

    @action(methods=['put'], detail=True)
    def reject(self, request, uuid=None, *args, **kwargs):
        return self.__accept_or_reject(request, uuid, False)

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

    @action(methods=['get'], detail=False, permission_classes=[IsAuthenticated, IsProfessional])
    def received(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            self.queryset.filter(professional=request.user.professional),
            many=True,
            context={'request': request}
        )
        return Response(serializer.data)

    def destroy(self, request, uuid=None, *args, **kwargs):
        proposal = get_object_or_404(self.queryset, uuid=uuid)
        if proposal.client == request.user and not proposal.accepted:
            return Response({'deleted': proposal.delete()[0]})
        return Response({'error': 'Unauthorized'}, status=403)

    @action(methods=['get'], detail=True)
    def counter(self, request, uuid=None, *args, **kwargs):
        proposal = get_object_or_404(self.queryset, uuid=uuid)
        serializer = serializers.CounterProposalSerializer(
            proposal.counter_proposal,
            context={'request': request},
            many=False,
        )
        return Response(serializer.data)

    @counter.mapping.post
    def create_counter(self, request, uuid=True, *args, **kwargs):
        if request.user.professional != self.object.professional:
            return Response({'error': 'Unauthorized'}, status=400)
        serializer = serializers.CounterProposalSerializer(
            data={**request.data, 'proposal': uuid,},
            context={'request': request}
        )
        if serializer.is_valid():
            serializer.instance = serializer.create(serializer.validated_data)
            serializer.instance.full_clean()
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

    @counter.mapping.put
    def update_counter(self, request, uuid=None, *args, **kwargs):
        if request.user.professional != self.object.professional:
            return Response({'error': 'Unauthorized'}, status=400)
        counter_proposal = get_object_or_404(models.CounterProposal, proposal__uuid=uuid, _accepted__isnull=True)
        serializer = serializers.CounterProposalSerializer(
            data={**request.data, 'proposal': uuid,},
            context={'request': request},
            instance=counter_proposal,
        )
        if serializer.is_valid():
            serializer.update(counter_proposal, serializer.validated_data)
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    @counter.mapping.patch
    def accept_or_reject_counter(self, request, uuid=None, *args, **kwargs):
        if not 'accept' in request.data or type(request.data.get('accept')) != bool:
            return Response({'error': '"accept" field is required'}, status=400)
        if self.object.client != request.user:
            return Response({'error': 'Unauthorized'}, status=403)
        counter_proposal = get_object_or_404(
            models.CounterProposal,
            proposal__uuid=uuid,
            _accepted__isnull=True,
            proposal__client=request.user,
        )
        if request.data.get('accept') == True:
            counter_proposal.accept()
        else:
            counter_proposal.reject()
        serializer = serializers.CounterProposalSerializer(counter_proposal)
        return Response(serializer.data)

    @counter.mapping.delete
    def destroy_counter(self, request, uuid=None, *args, **kwargs):
        counter_proposal = get_object_or_404(
            models.CounterProposal,
            proposal__uuid=uuid,
            _accepted__isnull=True,
            proposal__professional=request.user.professional
        )
        return Response({'deleted': counter_proposal.delete()[0]})

class JobViewSet(ViewSet):
    serializer_class = serializers.JobSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'uuid'
    professional_actions = ('list',)

    def get_permissions(self):
        if self.action in self.professional_actions:
            return [IsAuthenticated(), IsProfessional()]
        return super().get_permissions()

    @property
    def queryset(self):
        return models.Job.objects.filter(
            Q(professional__user=self.request.user, proposal__professional__user=self.request.user) |
            Q(client=self.request.user, proposal__client=self.request.user)
        ).all()

    def list(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            request.user.professional.jobs.all(),
            many=True,
            context={'request': request}
        )
        return Response(serializer.data)

    @action(methods=['get'], detail=False)
    def hires(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            request.user.hires.all(),
            many=True,
            context={'request': request}
        )
        return Response(serializer.data)

    def retrieve(self, request, uuid, *args, **kwargs):
        job = get_object_or_404(self.queryset, uuid=uuid)
        serializer = self.serializer_class(job, context={'request': request})
        return Response(serializer.data)

    def destroy(self, request, uuid, *args, **kwargs):
        job: models.Job = get_object_or_404(self.queryset, Q(payment__paid=False) | Q(payment__isnull=True), uuid=uuid,)
        return Response({'deleted': job.delete()[0]})
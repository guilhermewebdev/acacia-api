from rest_framework import serializers
from . import models
from core.serializers import PublicProfessionalSerializer, CreationUserSerializer
class ProposalSerializer(serializers.ModelSerializer):
    client = serializers.SlugRelatedField(
        slug_field='uuid',
        many=False,
        queryset=models.User.objects.filter(is_active=True).all()
    )
    professional = serializers.SlugRelatedField(
        slug_field='uuid',
        many=False,
        queryset=models.Professional.objects.filter(user__is_active=True).all()
    )
    job = serializers.SlugRelatedField(
        slug_field='uuid',
        many=False,
        read_only=True,
    )

    class Meta:
        model = models.Proposal
        fields = (
            'uuid',
            'city',
            'state',
            'professional_type',
            'service_type',
            'start_datetime',
            'end_datetime',
            'value',
            'description',
            'registration_date',
            'professional',
            'client',
            'accepted',
            'job',
        )
        read_only_fields = (
            'uuid',
            'registration_date',
            'accepted',
        )

class CounterProposalSerializer(serializers.ModelSerializer):
    proposal = serializers.SlugRelatedField(
        slug_field='uuid',
        many=False,
        queryset=models.Proposal.objects.all()
    )

    class Meta:
        model = models.CounterProposal
        fields = (
            'uuid',
            'proposal',
            'value',
            'description',
            'registration_date',
            'accepted',
        )
        read_only_fields = (
            'accepted',
            'registration_date',
            'uuid',
        )

class JobSerializer(serializers.ModelSerializer):
    proposal = serializers.SlugRelatedField(
        slug_field='uuid',
        many=False,
        queryset=models.Proposal.objects.all()
    )
    client = serializers.SlugRelatedField(
        slug_field='uuid',
        many=False,
        queryset=models.User.objects.filter(is_active=True).all()
    )
    professional = serializers.SlugRelatedField(
        slug_field='uuid',
        many=False,
        queryset=models.Professional.objects.filter(user__is_active=True).all()
    )

    class Meta:
        model = models.Job
        fields = (
            'uuid',
            'proposal',
            'professional',
            'client',
            'value',
            'start_datetime',
            'end_datetime',
            'registration_date',
        )
        read_only_fields = (
            'uuid',
            'registration_date',
        )
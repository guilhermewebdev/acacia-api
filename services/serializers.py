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
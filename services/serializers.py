from rest_framework import serializers
from . import models

class ProposalSerializer(serializers.ModelSerializer):

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
        )
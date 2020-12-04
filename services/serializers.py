from rest_framework import serializers
from . import models

class ProposalSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = models.Proposal
        fields = (
            'city',
            'state',
            'professional_type',
            'service_type',
            'start_datetime',
            'end_datetime',
            'value',
            'description',
            'registration_date',
            'url',
        )
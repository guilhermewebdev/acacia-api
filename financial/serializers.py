from rest_framework import serializers
from . import models

class PaymentSerializer(serializers.ModelSerializer):
    transaction = serializers.JSONField()
    card_index = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = models.Payment
        fields = (
            'uuid',
            'client',
            'professional',
            'value',
            'job',
            'registration_date',
            'paid',
            'transaction',
        )
        read_only_fields = (
            'uuid',
            'registration_date',
            'paid',
            'transaction',
        )
        extra_kwargs = {
            'client': {'write_only': True},
            'professional': {'write_only': True},
            'job': {'write_only': True},
        }
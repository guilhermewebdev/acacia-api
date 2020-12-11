from rest_framework import serializers
from . import models

class PaymentSerializer(serializers.ModelSerializer):
    transaction = serializers.JSONField(read_only=True)
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
            'card_index',
        )
        read_only_fields = (
            'uuid',
            'client',
            'professional',
            'value',
            'job',
            'registration_date',
            'paid',
            'transaction',
        )

class CashOutSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = models.CashOut
        fields = (
            'value',
            'withdrawn',
            
        )
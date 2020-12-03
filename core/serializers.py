from rest_framework import serializers
from . import models

class PublicUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.User
        fields = (
            'full_name',
            'uuid',
            'email',
            'avatar',
            'is_active',
        )
        lookup_field = 'uuid'

class PublicProfessionalSerializer(serializers.HyperlinkedModelSerializer):
    user = PublicUserSerializer(many=False, read_only=True)
    full_name = serializers.CharField(max_length=200, write_only=True)
    email = serializers.EmailField(write_only=True)
    password1 = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)
    cpf = serializers.CharField(write_only=True)
    rg = serializers.CharField(write_only=True)
    address = serializers.CharField(write_only=True)
    zip_code = serializers.CharField(write_only=True)
    coren = serializers.CharField(write_only=True)

    class Meta:
        model = models.Professional
        fields = (
            'uuid',
            'user',
            'about',
            'avg_price',
            'state',
            'city',
            'occupation',
            'skills',
            'avg_rating',
            'availabilities',
            'password1',
            'password2',
            'full_name',
            'email',
            'cpf',
            'rg',
            'address',
            'zip_code',
            'coren',
        )
        read_only_fields = (
            'about',
            'avg_price',
            'skills',
            'avg_rating',
            'availabilities',
        )
        lookup_field = 'uuid'


class PrivateProfessionalSerializer(serializers.ModelSerializer):
    cash = serializers.FloatField(read_only=True)
    avg_rating = serializers.IntegerField(read_only=True)
    recipient = serializers.JSONField(read_only=True)

    class Meta:
        model = models.Professional
        fields = (
            'uuid',
            'about',
            'avg_price',
            'state',
            'city',
            'address',
            'zip_code',
            'cpf',
            'rg',
            'occupation',
            'skills',
            'coren',
            'saved_in_pagarme',
            'recipient',
            'avg_rating',
            'cash',
        )
        read_only_fields = (
            'cash',
            'avg_rating',
            'recipient',
            'uuid',
            'saved_in_pagarme',
        )
        lookup_field = 'uuid'

class PrivateUserSerializer(serializers.ModelSerializer):
    professional = PrivateProfessionalSerializer(many=False, read_only=False)
    is_professional = serializers.BooleanField(read_only=True)    
    costumer = serializers.JSONField(read_only=True)

    class Meta:
        model = models.User
        fields = (
            'uuid',
            'full_name',
            'email',
            'born',
            'avatar',
            'cellphone_ddd',
            'cellphone',
            'telephone_ddd',
            'telephone',
            'saved_in_pagarme',
            'is_active',
            'is_professional',
            'customer',
            'professional',
            'costumer',
        )
        read_only_fields = (
            'is_active',
            'is_professional',
            'costumer',
            'uuid',
            'saved_in_pagarme',
        )
        lookup_field = 'uuid'

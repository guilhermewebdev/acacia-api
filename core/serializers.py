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

class PublicProfessionalSerializer(serializers.HyperlinkedModelSerializer):
    user = PublicUserSerializer(many=False, read_only=True)
    full_name = serializers.CharField(max_length=200, write_only=True)
    email = serializers.EmailField(write_only=True)
    password1 = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)
    cpf = serializers.CharField(write_only=True)
    rg = serializers.CharField(write_only=True)

    class Meta:
        model = models.Professional
        fields = (
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
            'rg'
        )
        read_only_fields = (
            'about',
            'avg_price',
            'skills',
            'avg_rating',
            'availabilities',
        )
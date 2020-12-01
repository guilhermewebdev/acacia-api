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
        )
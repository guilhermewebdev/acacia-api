from core.forms import ERROR_MESSAGES
from django.core.exceptions import ValidationError
from rest_framework import serializers
from . import models

class AvailabilitiesSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = models.Availability
        fields = (
            'uuid',
            'start_datetime',
            'end_datetime',
            'recurrence',
            'weekly_recurrence',
            'registration_date',
        )
        read_only_fields = (
            'registration_date',
            'uuid',
        )


class AddressSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Address
        fields = (
            'street',
            'street_number',
            'zipcode',
            'state',
            'city',
            'neighborhood',
            'complementary',
        )

class PublicProfessionalSerializer(serializers.HyperlinkedModelSerializer):
    full_name = serializers.CharField(source='user.full_name', max_length=200)
    email = serializers.EmailField(source='user.email')
    avatar = serializers.ImageField(source='user.avatar', read_only=True)
    is_active = serializers.BooleanField(source='user.is_active', read_only=True)
    password1 = serializers.CharField(write_only=True, required=True)
    password2 = serializers.CharField(write_only=True, required=True)
    cpf = serializers.CharField(write_only=True)
    address = AddressSerializer(write_only=True)
    coren = serializers.CharField(write_only=True)
    url = serializers.SerializerMethodField('get_url')

    def get_url(self, obj):
        request = self.context['request']
        return request.build_absolute_uri(f'/professionals/{obj.uuid}/')
    
    def validate(self, attrs):
        if attrs.get('password1') != attrs.get('password2'):
            raise ValidationError(
                ERROR_MESSAGES['password_mismatch'],
                code='password_mismatch',
            )
        return super().validate(attrs)

    def create(self, validated_data):
        validated_data.pop('password2')
        user:models.User = models.User.objects.create_user(
            email=validated_data.pop('email'),
            full_name=validated_data.pop('full_name'),
            password=validated_data.pop('password1'),
            cpf=validated_data.pop('cpf'),
        )
        user.full_clean()
        address = models.Address(
            **validated_data.pop('address'),
            user=user,
        )
        address.full_clean()
        self.instance = models.Professional(
            **validated_data,
            user=user,
        )
        self.instance.full_clean()
        return self.instance

    def save(self, **kwargs):
        super().save(**kwargs)
        self.instance.user.confirm_email()

    class Meta:
        model = models.Professional
        fields = (
            'uuid',
            'full_name',
            'email',
            'password1',
            'password2',
            'is_active',
            'avatar',
            'cpf',
            'about',
            'avg_price',
            'occupation',
            'skills',
            'avg_rating',
            'address',
            'coren',
            'url',
        )
        read_only_fields = (
            'about',
            'avg_price',
            'skills',
            'avg_rating',
            'availabilities',
            'is_active',
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.context['request'].user.is_professional:
            self.fields.pop('professional')

    def update(self, instance, validated_data):
        if instance.is_professional and 'professional' in validated_data:
            serializer = PrivateProfessionalSerializer(
                instance=instance.professional,
                data=validated_data.pop('professional')
            )
            if serializer.is_valid():
                serializer.update(instance.professional, serializer.validated_data)
                instance.professional = serializer.instance
        return super().update(instance, validated_data)
        
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

class CreationUserSerializer(serializers.ModelSerializer):
    password1 = serializers.CharField(write_only=True, required=True)
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = models.User
        fields = (
            'uuid',
            'password1',
            'password2',
            'full_name',
            'email',
            'is_active',
        )
        read_only_fields = (
            'is_active',
            'uuid',
        )
        lookup_field = 'uuid'
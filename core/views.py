from os import stat

from pagarme import recipient
from core.models import Availability
from core.serializers import AvailabilitiesSerializer
from django.db.models.query_utils import Q
from . import models, serializers, forms
import datetime
from rest_framework import viewsets, mixins
from django.contrib.postgres.search import SearchVector
from django.utils.dateparse import parse_time, parse_date
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework.decorators import action, permission_classes
from rest_framework.permissions import BasePermission, IsAuthenticated, AllowAny

def get_week(date: str) -> int:
    if not date: return None
    return datetime.datetime.strftime(date, "%Y-%m-%d").weekday()

def get_day(date: str) -> int:
    if not date: return None
    return datetime.datetime.strftime(date, "%Y-%m-%d").day

def professional_postback(request, uuid):
    pass

class IsProfessional(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_professional

class Professionals(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet):
    model = models.Professional
    serializer_class = serializers.PublicProfessionalSerializer
    lookup_field = 'uuid'
    queryset = models.Professional.objects.filter(user__is_active=True).all()

    @property
    def paginated_by(self):
        return int(self.request.GET.get('limit', [10])[0])

    def list(self, request, *args, **kwargs):
        verify_dict = lambda dic: dict(filter(lambda item: item[1] != None and item[1] != [None], dic.items()))
        filters = {
            **self.request.GET,
            'start_time': parse_time(self.request.GET.get('start_time', '')),
            'start_date': parse_date(self.request.GET.get('start_date', '')),
            'end_time': parse_time(self.request.GET.get('end_time', '')),
            'end_date': parse_date(self.request.GET.get('end_date', '')),
            'skills': self.request.GET.get('skills'),
        }
        filter_by_date = verify_dict(dict(
            availabilities__start_datetime__time__gte=filters.get('start_time'),
            availabilities__start_datetime__date__gte=filters.get('start_date'),
            availabilities__end_datetime__time__lte=filters.get('end_time'),
            availabilities__end_datetime_date__lte=filters.get('end_date'),
            availabilities__recurrence__isnull=True,
        ))
        filter_by_time = verify_dict(dict(
            availabilities__start_datetime__time__gte=filters.get('start_time'),
            availabilities__end_datetime__time__lte=filters.get('end_time'),
            availabilities__recurrence='D',
        ))
        filter_by_week_day = verify_dict(dict(
            availabilities__start_datetime__time__gte=filters.get('start_time'),
            availabilities__start_datetime__date__iso_week_day=get_week(filters.get('start_date')),
            availabilities__end_datetime__time__lte=filters.get('end_time'),
            availabilities__end_datetime_date__iso_week_day=get_week(filters.get('end_date')),
            availabilities__recurrence='W',
        ))
        filter_by_day = verify_dict(dict(
            availabilities__start_datetime__time__gte=filters.get('start_time'),
            availabilities__start_datetime__date__day=get_day(filters.get('start_date')),
            availabilities__end_datetime__time__lte=filters.get('end_time'),
            availabilities__end_datetime_date__day=get_day(filters.get('end_date')),
            availabilities__recurrence='M',
        ))
        filter_by_attrs = verify_dict(dict(
            user__is_active=True,
            skills__overlap=filters.get('skills'),
            user__address__city__search=list(filters.get('city', [None]))[0],
            user__address__state=list(filters.get('state', [None]))[0],
            occupation=list(filters.get('occupation', [None]))[0],
            search=filters.get('search', [None])[0],
        ))
        queryset = self.queryset.annotate(
                search=SearchVector('user__full_name', 'occupation', 'skills', 'coren', 'about', 'user__email', 'user__address__city')
            ).filter(
            Q(**filter_by_date) | Q(**filter_by_time) | 
            Q(**filter_by_week_day) | Q(**filter_by_day),
            **filter_by_attrs
        )
        serializer = self.serializer_class(queryset, many=True, context={'request': request})
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.instance = serializer.create(serializer.validated_data)
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    def retrieve(self, request, uuid=None, *args, **kwargs):
        professional = get_object_or_404(self.queryset, uuid=uuid)
        serializer = self.serializer_class(instance=professional, context={'request': request})
        return Response(serializer.data)

    @action(methods=['get'], detail=True)
    def availabilities(self, request, uuid, *args, **kwargs):
        availabilities = models.Availability.objects.filter(
            professional__uuid=uuid,
            professional__user__is_active=True
        ).all()
        serializer = serializers.AvailabilitiesSerializer(
            availabilities, many=True,
        )
        return Response(serializer.data)


class Users(viewsets.ViewSet):
    model = models.User
    lookup_field = 'uuid'
    auth_actions = ('customer', 'create_customer', 'availabilities', 'put', 'get', 'patch', 'delete')
    auth_methods = ('PUT', 'GET', 'PATCH', 'DELETE')
    allowed_actions = ('activate',)
    __serializer = None

    @property
    def serializer_class(self):
        if not self.__serializer:
            if self.action in self.auth_actions or self.request.method in self.auth_methods:
                self.__serializer = serializers.PrivateUserSerializer
            else: self.__serializer = serializers.CreationUserSerializer
        return self.__serializer
    
    @serializer_class.setter
    def serializer(self, value):
        self.__serializer = value

    def get_permissions(self):
        if self.action in self.allowed_actions:
            return (AllowAny(),)
        if self.action in self.auth_actions or self.request.method in self.auth_methods:
            return (IsAuthenticated(),)
        return super(Users, self).get_permissions()

    def get(self, request, *args, **kwargs):
        serializer = self.serializer_class(instance=request.user, many=False, context={'request': request})
        return Response(data=serializer.data)

    def put(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            data=request.data,
            context={'request': request},
            instance=request.user
        )
        if serializer.is_valid():
            serializer.update(request.user, serializer.validated_data)
            return Response(data=serializer.data)
        return Response(data=serializer.errors, status=400)

    def delete(self, request, *args, **kwargs):
        form = forms.UserDeletionForm(data=request.data, instance=request.user)
        if form.is_valid():
            return Response(data={'deleted': form.save()})
        return Response(data=form.errors, status=400, exception=form.error_class())

    def patch(self, request, *args, **kwargs):
        form = forms.PasswordChangeForm(data=request.data, instance=request.user)
        if form.is_valid():
            form.save()
            serializer = self.serializer_class(instance=form.instance, many=False, context={'request': request})
            return Response(data=serializer.data)
        return Response(data=form.errors, exception=form.error_class(), status=400)

    def create(self, request, *args, **kwargs):
        form = forms.UserCreationForm(data=request.data)
        if form.is_valid():
            form.save()
            serializer = self.serializer_class(instance=form.instance, many=False, context={'request': request})
            return Response(serializer.data)
        return Response(data=form.errors, status=400, exception=form.error_class())

    @action(methods=['put'], detail=True)
    def activate(self, request, uuid=None, *args, **kwargs):
        form = forms.UserActivationForm(data={
            'uuid': uuid,
            'token': request.data.get('token'),
        })
        if form.is_valid():
            request.user = form.save()
            serializer = self.serializer_class(instance=request.user, many=False, context={'request': request})
            return Response(data=serializer.data)
        return Response(data=form.errors, status=400, exception=form.error_class())

    @action(methods=['get'], detail=False)
    def customer(self, request, *args, **kwargs):
        user: models.User = request.user
        return Response(user.customer, content_type='application/json')

    @customer.mapping.post
    def create_customer(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            data=request.data,
            context={'request': request},
            instance=request.user
        )
        if serializer.is_valid():
            serializer.update(request.user, serializer.validated_data)
        customer = request.user.create_customer()
        return Response(customer)

    @action(methods=['get'], detail=False)
    def cards(self, request, *args, **kwargs):
        return Response(request.user.cards)

    @cards.mapping.post
    def create_card(self, request, *args, **kwargs):
        form = forms.CardForm(data=request.data)
        if form.is_valid():
            data = request.user.create_card(form.full_cleaned_data)
            return Response(data=data)
        return Response(form.errors, status=400)

    @action(methods=['get'], detail=False, permission_classes=[IsAuthenticated, IsProfessional])
    def recipient(self, request, *args, **kwargs):
        return Response(data=request.user.professional.recipient)

    @recipient.mapping.post
    def create_recipient(self, request, *args, **kwargs):
        pass

class PrivateAvailabilities(viewsets.ViewSet):
    lookup_field = 'uuid'
    permission_classes = [IsAuthenticated, IsProfessional]
    basename = 'SelfAvailabilities'

    @property
    def queryset(self):
        return self.request.user.professional.availabilities.all()

    def list(self, request, *args, **kwargs):
        serializer = serializers.AvailabilitiesSerializer(
            request.user.professional.availabilities.all(),
            many=True,
        )
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        form = forms.AvailabilityForm({
            **request.data,
            'professional': request.user.professional
        })
        if form.is_valid():
            form.save()
            serializer = AvailabilitiesSerializer(form.instance)
            return Response(serializer.data)
        return Response(form.errors, status=400, exception=form.error_class())

    def retrieve(self, request, uuid, *args, **kwargs):
        availability = get_object_or_404(self.queryset, uuid=uuid)
        serializer = AvailabilitiesSerializer(instance=availability, many=False)
        return Response(serializer.data)
        
    def update(self, request, uuid, *args, **kwargs):
        availability = get_object_or_404(self.queryset, uuid=uuid)
        form = forms.AvailabilityForm({
            **request.data,
            'professional': request.user.professional
        }, instance=availability)
        if form.is_valid():
            form.save()
            serializer = AvailabilitiesSerializer(form.instance)
            return Response(serializer.data)
        return Response(form.errors, status=400, exception=form.error_class())

    def destroy(self, request, uuid, *args, **kwargs):
        availability = get_object_or_404(self.queryset, uuid=uuid)
        deletions = availability.delete()
        return Response({'deleted': deletions[0]})

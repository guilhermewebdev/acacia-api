from django.db.models.query_utils import Q
from . import models, serializers, forms
import datetime
from rest_framework import viewsets
from django.contrib.postgres.search import SearchVector
from django.utils.dateparse import parse_time, parse_date
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

def get_week(date: str) -> int:
    if not date: return None
    return datetime.datetime.strftime(date, "%Y-%m-%d").weekday()

def get_day(date: str) -> int:
    if not date: return None
    return datetime.datetime.strftime(date, "%Y-%m-%d").day

def professional_postback(request, uuid):
    pass

class Professionals(viewsets.ModelViewSet):
    model = models.Professional
    serializer_class = serializers.PublicProfessionalSerializer
    queryset = models.Professional.objects.filter(user__is_active=True).all()
    lookup_field = 'uuid'

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
            city__search=list(filters.get('city', [None]))[0],
            state=list(filters.get('state', [None]))[0],
            occupation=list(filters.get('occupation', [None]))[0],
        ))
        queryset = self.queryset.annotate(
                search=SearchVector('user__full_name', 'occupation', 'skills', 'coren', 'about', 'user__email')
            ).filter(
            Q(**filter_by_date) | Q(**filter_by_time) | 
            Q(**filter_by_week_day) | Q(**filter_by_day),
            **filter_by_attrs
        )
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)

    def create(self, request):
        form = forms.ProfessionalCreationForm(data=request.data)
        if form.is_valid():
            professional = form.save()
            serializer = self.serializer_class(professional, many=False)
            return Response(serializer.data)
        return Response(form.errors, status=400)

    def retrieve(self, request, uuid=None):
        professional = get_object_or_404(self.queryset, uuid=uuid)
        serializer = self.serializer_class(professional)
        return Response(serializer.data)    


class Users(viewsets.ViewSet):
    model = models.User
    lookup_field = 'uuid'
    auth_actions = ('profile', 'update')

    @property
    def serializer_class(self):
        if self.action in self.auth_actions:
            return serializers.PrivateUserSerializer
        return serializers.CreationUserSerializer

    def get_permissions(self):
        if self.action in self.auth_actions:
            return (IsAuthenticated(),)
        return super(Users, self).get_permissions()

    @action(methods=['get'], detail=False)
    def profile(self, request, uuid=None, *args, **kwargs):
        serializer = self.serializer_class(instance=request.user, many=False)
        return Response(data=serializer.data)

    @action(methods=['put'], detail=False)
    def profile(self, request, *args, **kwargs):
        form = forms.UserChangeForm(data=request.data)
        if form.is_valid():
            form.save()
            serializer = self.serializer_class(instance=form.instance)
            return Response(data=serializer.data)
        return Response(exception=form.errors, status=400)

    def create(self, request, *args, **kwargs):
        form = forms.UserCreationForm(data=request.data)
        if form.is_valid():
            form.save()
            serializer = self.serializer_class(instance=form.instance)
            return Response(serializer.data)
        return Response(form.errors, status=400)
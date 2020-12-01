from django.db.models.query_utils import Q
from api.utils import JSONList
from django.views.generic.list import ListView
from . import models
import datetime
from django.contrib.postgres.search import SearchVector
from django.utils.dateparse import parse_time, parse_date


def get_week(date: str) -> int:
    if not date: return None
    return datetime.datetime.strftime(date, "%Y-%m-%d").weekday()

def get_day(date: str) -> int:
    if not date: return None
    return datetime.datetime.strftime(date, "%Y-%m-%d").day

def professional_postback(request, uuid):
    pass

class ProfessionalList(JSONList, ListView):
    model = models.Professional

    @property
    def paginated_by(self):
        return int(self.request.GET.get('limit', [10])[0])

    def get_queryset(self):
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
        return models.Professional.objects.annotate(
                search=SearchVector('user__full_name', 'occupation', 'skills', 'coren', 'about', 'user__email')
            ).filter(
            Q(**filter_by_date) | Q(**filter_by_time) | 
            Q(**filter_by_week_day) | Q(**filter_by_day),
            **filter_by_attrs
        )
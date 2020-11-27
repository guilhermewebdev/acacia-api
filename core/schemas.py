from django.db.models.query_utils import Q
import graphene
from graphene.types.inputobjecttype import InputObjectType
from . import forms, models
from graphene_django import DjangoObjectType
from graphene_django.forms.mutation import DjangoFormMutation, DjangoModelFormMutation
from graphql_jwt.decorators import login_required
from django.utils.translation import gettext as _
import datetime
from django.contrib.postgres.search import SearchVector
from api.utils import PaginationType, pagination


def get_week(date: str) -> int:
    if not date: return None
    return datetime.datetime.strftime(date, "%Y-%m-%d").weekday()

def get_day(date: str) -> int:
    if not date: return None
    return datetime.datetime.strftime(date, "%Y-%m-%d").day


class ProfessionalType(DjangoObjectType):
    recipient = graphene.Field(graphene.JSONString)
    avg_rating = graphene.Field(graphene.Int)
    cash = graphene.Field(graphene.Float)
    avg_price = graphene.Field(graphene.Float, required=False)

    def resolve_user(parent, info):
        return parent.user

    def resolve_availabilities(parent, info):
        return parent.availabilities.all()

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
            'coren',
            'recipient',
            'avg_rating',
            'availabilities',
        )

class UserType(DjangoObjectType):
    is_professional = graphene.Field(graphene.Boolean)
    customer = graphene.Field(graphene.JSONString)
    professional = graphene.Field(ProfessionalType, required=False)

    def resolve_professional(parent, info):
        return parent.professional or None

    class Meta:
        model = models.User
        fields = (
            'full_name',
            'uuid',
            'is_active',
            'email',
            'born',
            'avatar',
            'celphone_ddd',
            'celphone',
            'telephone_ddd',
            'telephone',
            'saved_in_pagarme',
            'is_professional',
            'customer',
            'date_joined',
            'professional',
        )

class UserCreation(DjangoModelFormMutation):
    user = graphene.Field(UserType)

    class Meta:
        form_class = forms.UserCreationForm
        return_field_name = 'user'

class UserUpdate(DjangoModelFormMutation):
    user = graphene.Field(UserType)

    @classmethod
    @login_required
    def mutate(cls, root, info, input):
        return super().mutate(root, info, input)

    @classmethod
    def get_form_kwargs(cls, root, info, **input):
        kwargs = super().get_form_kwargs(root, info, **input)
        kwargs['instance'] = info.context.user
        return kwargs

    class Meta:
        form_class = forms.UserChangeForm
        return_field_name = 'user'

class PasswordReset(DjangoFormMutation):
    sent = graphene.Boolean()
    class Meta:
        form_class = forms.PasswordResetForm
        return_field_name = 'sent'

class UserActivation(DjangoFormMutation):
    is_active = graphene.Field(graphene.Boolean, required=True)

    @classmethod
    def perform_mutate(cls, form, info):
        return cls(errors=[], is_active=form.save())
    class Meta:
        form_class = forms.UserActivationForm

class UserDeletion(DjangoModelFormMutation):
    deleted = graphene.Field(graphene.Boolean, required=True)

    @classmethod
    @login_required
    def mutate(cls, root, info, input):
        return super().mutate(root, info, input)

    @classmethod
    def perform_mutate(cls, form, info):
        return cls(deleted=form.save(), errors=[])

    @classmethod
    def get_form_kwargs(cls, root, info, **input):
        return {
            "data": input,
            "instance": info.context.user
        }

    class Meta:
        form_class = forms.UserDeletionForm

class ProfessionalCreation(DjangoModelFormMutation):
    professional = graphene.Field(ProfessionalType)

    @classmethod
    def perform_mutate(cls, form, info):
        return cls(professional=form.save())

    @classmethod
    def get_form_kwargs(cls, root, info, **input):
        return {"data": input}

    class Meta:
        form_class = forms.ProfessionalCreationForm
        return_field_name = 'professional'

class ProfessionalUpdate(DjangoModelFormMutation):
    professional = graphene.Field(ProfessionalType)
    
    @classmethod
    @login_required
    def mutate(cls, root, info, input):
        return super().mutate(root, info, input)

    @classmethod
    def get_form_kwargs(cls, root, info, **input):
        return {
            "data": input,
            "instance": info.context.user.professional
        }

    class Meta:
        form_class = forms.ProfessionalUpdateForm
        return_field_name = 'professional'

class ProfessionalDeletion(DjangoFormMutation):
    deleted = graphene.Field(graphene.Boolean)

    @classmethod
    @login_required
    def mutate(cls, root, info, input):
        return super().mutate(root, info, input)

    @classmethod
    def perform_mutate(cls, form, info):
        return cls(deleted=form.save(), errors=[])        

    @classmethod
    def get_form_kwargs(cls, root, info, **input):
        return {
            "data": input,
            "instance": info.context.user.professional
        }
    class Meta:
        form_class = forms.ProfessionalDeletionForm


class PasswordChange(DjangoModelFormMutation):
    changed = graphene.Field(graphene.Boolean)

    @classmethod
    @login_required
    def mutate(cls, root, info, input):
        return super().mutate(root, info, input)

    @classmethod
    def get_form_kwargs(cls, root, info, **input):
        return {
            "data": input,
            "instance": info.context.user
        }    
    class Meta:
        form_class = forms.PasswordChangeForm
        return_field_name = 'changed'

class Mutation(graphene.ObjectType):
    create_user = UserCreation.Field(description=_('Create a new user client, it\'s need be unique'))
    update_user = UserUpdate.Field(description=_('Update yourself user account, you need be authenticated'))
    delete_user = UserDeletion.Field(description=_('Delete yourself account'))
    create_professional = ProfessionalCreation.Field(description=_('Create a new professional account, it\'s need be unique'))
    update_professional = ProfessionalUpdate.Field(description=_('Update yourself professional account, you need be authenticated'))
    delete_professional = ProfessionalDeletion.Field(description=_('Delete yourself professional account'))
    activate_user = UserActivation.Field(description=_('Check user email token, to activate your account'))
    reset_password = PasswordReset.Field(description=_('If you lost the password, you can reset it here'))
    change_password = PasswordChange.Field(description=_('Update youself password'))


class FilterProfessionalInput(InputObjectType):
    city = graphene.String()
    state = graphene.String()
    occupation = graphene.String()
    skill = graphene.String()
    start_date = graphene.Date()
    start_time = graphene.Time()
    end_date = graphene.Date()
    end_time = graphene.Time()
    search = graphene.String()


class ProfessionalPagination(PaginationType):
    data = graphene.List(ProfessionalType, filters=FilterProfessionalInput())


class Query(graphene.ObjectType):
    professionals = graphene.Field(ProfessionalPagination, offset=graphene.Int(), limit=graphene.Int())

    @pagination(ProfessionalPagination)
    def resolve_professionals(root, info, **filters):
        verify_dict = lambda dic: dict(filter(lambda item: item[1] != None and item[1] != [None], dic.items()))
        filter_by_date = verify_dict(dict(
            availabilities__start_time__gte=filters.get('start_time'),
            availabilities__start_date__gte=filters.get('start_date'),
            availabilities__end_time__lte=filters.get('end_time'),
            availabilities__end_date__lte=filters.get('end_date'),
            availabilities__recurrence__isnull=True,
        ))
        filter_by_time = verify_dict(dict(
            availabilities__start_time__gte=filters.get('start_time'),
            availabilities__end_time__lte=filters.get('end_time'),
            availabilities__recurrence='D',
        ))
        filter_by_week_day = verify_dict(dict(
            availabilities__start_time__gte=filters.get('start_time'),
            availabilities__start_date__iso_week_day=get_week(filters.get('start_date')),
            availabilities__end_time__lte=filters.get('end_time'),
            availabilities__end_date__iso_week_day=get_week(filters.get('end_date')),
            availabilities__recurrence='W',
        ))
        filter_by_day = verify_dict(dict(
            availabilities__start_time__gte=filters.get('start_time'),
            availabilities__start_date__day=get_day(filters.get('start_date')),
            availabilities__end_time__lte=filters.get('end_time'),
            availabilities__end_date__day=get_day(filters.get('end_date')),
            availabilities__recurrence='M',
        ))
        filter_by_attrs = verify_dict(dict(
            user__is_active=True,
            skills__overlap=[filters.get('skill')],
            city__search=filters.get('city'),
            state=filters.get('state'),
            occupation=filters.get('occupation'),
        ))
        return models.Professional.objects.annotate(
                search=SearchVector('user__full_name', 'occupation', 'skills', 'coren', 'about', 'user__email')
            ).filter(
            Q(**filter_by_date) | Q(**filter_by_time) | 
            Q(**filter_by_week_day) | Q(**filter_by_day),
            **filter_by_attrs
        )
import graphene
from pagarme import recipient
from . import forms, models
from graphene_django import DjangoObjectType
from graphene_django.forms.mutation import DjangoFormMutation, DjangoModelFormMutation
from graphql_jwt.decorators import login_required
from django.forms.models import model_to_dict

class ProfessionalType(DjangoObjectType):
    recipient = graphene.Field(graphene.JSONString)
    avg_rating = graphene.Field(graphene.Int)
    cash = graphene.Field(graphene.Float)
    avg_price = graphene.Field(graphene.Float, required=False)

    def resolve_user(parent, info):
        return parent.user

    class Meta:
        model = models.Professional
        fields = (
            'user',
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

class UserDeletion(DjangoFormMutation):
    deleted = graphene.Field(graphene.Boolean, required=True)

    @classmethod
    def perform_mutate(cls, form, info):
        form.clean()
        return cls(errors=[], password='', email='', deleted=form.save())
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

class Mutation(object):
    create_user = UserCreation.Field()
    update_user = UserUpdate.Field()
    reset_password = PasswordReset.Field()
    activate_user = UserActivation.Field()
    delete_user = UserDeletion.Field()
    create_professional = ProfessionalCreation.Field()
    update_professional = ProfessionalUpdate.Field()

import graphene
from graphene_django.types import ErrorType
from . import forms, models
from graphene_django import DjangoObjectType
from graphene_django.forms.mutation import DjangoFormMutation, DjangoModelFormMutation
from graphql_jwt.decorators import login_required
class UserType(DjangoObjectType):
    is_professional = graphene.Field(graphene.Boolean)
    customer = graphene.Field(graphene.JSONString)
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
    class Meta:
        form_class = forms.PasswordResetForm

class Mutation(object):
    create_user = UserCreation.Field()
    update_user = UserUpdate.Field()
    reset_password = PasswordReset.Field()
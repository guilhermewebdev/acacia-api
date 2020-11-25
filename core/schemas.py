import graphene
from . import forms, models
from graphene_django import DjangoObjectType
from graphene_django.forms.mutation import DjangoModelFormMutation

class UserType(DjangoObjectType):
    class Meta:
        model = models.User
        fields = (
            'full_name',
            'uuid',
            'is_active',
        )

class UserMutation(DjangoModelFormMutation):
    user = graphene.Field(UserType)

    class Meta:
        form_class = forms.CreationUserForm
        return_field_name = 'user'

class Mutation(object):
    create_user = UserMutation.Field()
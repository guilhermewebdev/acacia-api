import json
from django.core.serializers import serialize
from django.http import JsonResponse
from django.views.generic.base import View
from django.views.generic.edit import FormView
import graphene
from django.core.paginator import Paginator
from django.forms.models import model_to_dict


class PaginationType(graphene.ObjectType):
    page = graphene.Int()
    pages = graphene.Int()
    start_index = graphene.Int()
    end_index = graphene.Int()
    amount = graphene.Int()
    has_next = graphene.Boolean()
    has_previous = graphene.Boolean()
    has_other_pages = graphene.Boolean()


def pagination(ObjectType: PaginationType):
    def paginator(function):
        def resolver(root, info, offset:int=None, limit:int=None, *args, **kwargs):
            if offset and limit:
                pages = Paginator(function(root, info, *args, **kwargs), limit)
                page = pages.page(offset)
                return ObjectType(
                    page=page.number,
                    pages=pages.num_pages,
                    start_index=page.start_index(),
                    end_index=page.end_index(),
                    amount=pages.count,
                    has_next=page.has_next(),
                    has_previous=page.has_previous(),
                    has_other_pages=page.has_other_pages(),
                    data=page.object_list
                )
            return ObjectType(data=function(root, info, *args, **kwargs))
        return resolver
    return paginator



class JSONMixin:
    """
    A mixin that can be used to render a JSON response.
    """
    def render_to_json_response(self, context, **response_kwargs):
        """
        Returns a JSON response, transforming 'context' to make the payload.
        """
        return JsonResponse(
            self.get_data(context),
            **response_kwargs,
            safe=False,
        )

    def render_to_response(self, context, **response_kwargs):
        return self.render_to_json_response(context, **response_kwargs)


class JSONList(JSONMixin):

    def get_data(self, context):
        return json.loads(serialize('json', context.get('object_list')))

class JSONItem(JSONMixin):
    
    def get_data(self, context):
        return json.loads(model_to_dict(context.get('object')))
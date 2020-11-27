import graphene
from django.core.paginator import Paginator

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

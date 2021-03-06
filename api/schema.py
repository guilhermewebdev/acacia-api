from django.contrib.auth import login, logout
import graphene
import graphql_jwt
from core import schemas as core
class Mutation(core.Mutation):
    login = graphql_jwt.ObtainJSONWebToken.Field()
    logout = graphql_jwt.DeleteJSONWebTokenCookie.Field()
    verify_token = graphql_jwt.Verify.Field()
    refresh_token = graphql_jwt.Refresh.Field()
    delete_refresh_token_cookie = graphql_jwt.DeleteRefreshTokenCookie.Field()


class Query(core.Query):
    pass

schema = graphene.Schema(query=Query, mutation=Mutation)
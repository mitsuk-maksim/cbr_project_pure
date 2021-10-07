import graphene
# from django.contrib.auth import get_user_model
from graphql_auth.schema import UserQuery, MeQuery

from cbr_project_pure.functions import FieldResolver
from user.graphql.types import UserType



# class UserInfo(FieldResolver):
#     Output = UserType
#
#     @staticmethod
#     def query(parent, info):
#         return

class Query(UserQuery, MeQuery, graphene.ObjectType):
    # user_info = UserInfo.Field()
    pass

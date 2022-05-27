import graphene
from django.contrib.auth import get_user_model
from graphene_django import DjangoObjectType

from cbr_project_pure.graphql_base.base_types import NN, ID, String, ObjectType


class UserType(DjangoObjectType):
    class Meta:
        model = get_user_model()


class UserPureType(ObjectType):
    class Meta:
        model = get_user_model()

    id = NN(ID)
    username = String()
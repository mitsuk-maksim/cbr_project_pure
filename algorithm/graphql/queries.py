import graphene

from algorithm.graphql.types import AlhorithmType
from algorithm.models import Algorithm
from cbr_project_pure.functions import FieldResolver


class AlgorithmInfo(FieldResolver):
    class Arguments:
        id = graphene.Argument(graphene.ID, required=True)

    Output = AlhorithmType

    @staticmethod
    def query(parent, info, id: graphene.ID):
        algorithm = Algorithm.objects.get(id=id)
        return algorithm


class Query(graphene.ObjectType):
    algorithm_info = AlgorithmInfo.Field()

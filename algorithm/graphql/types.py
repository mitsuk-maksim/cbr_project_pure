import graphene
from algorithm.models import Algorithm, AlgorithmEnumType
from cbr_project_pure.graphql_base.base_types import Field, Enum

NN = graphene.NonNull

AlgorithmEnumType = Enum.from_enum(AlgorithmEnumType)


class AlgorithmType(graphene.ObjectType):
    class Meta:
        model = Algorithm

    id = NN(graphene.ID)
    title = NN(graphene.String)
    type = Field(AlgorithmEnumType)

import graphene
from algorithm.models import Algorithm

NN = graphene.NonNull


class AlhorithmType(graphene.ObjectType):
    class Meta:
        model = Algorithm

    id = NN(graphene.ID)
    title = NN(graphene.String)

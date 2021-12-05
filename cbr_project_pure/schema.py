import graphene

import user.schema
import dataset.schema
import result.schema
import algorithm.schema


class Query(
    algorithm.schema.Query,
    user.schema.Query
):
    pass


class Mutation(
    user.schema.Mutations,
    dataset.schema.Mutations
):
    pass


schema = graphene.Schema(query=Query, mutation=Mutation)

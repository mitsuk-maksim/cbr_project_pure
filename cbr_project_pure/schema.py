import graphene

import user.schema
import dataset.schema
import algorithm.schema
import result.schema


class Query(
    algorithm.schema.Query,
    user.schema.Query,
    dataset.schema.Query,
    result.schema.Query
):
    pass


class Mutation(
    user.schema.Mutations,
    dataset.schema.Mutations,
    algorithm.schema.Mutations
):
    pass


schema = graphene.Schema(query=Query, mutation=Mutation)

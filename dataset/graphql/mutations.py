# import graphene
from django.db import transaction

from cbr_project_pure.functions import CustomMutation
from cbr_project_pure.graphql_base.base_types import InputObjectType, String, Int, ListOf, Field, ObjectType
from dataset.graphql.types import DatasetType
from dataset.models import Dataset


class ParamInfoInput(InputObjectType):
    title = String(required=True)
    type = Int(required=True)
    description = String()


class DatasetCreateInput(InputObjectType):
    title = String(required=True)
    param_info = ListOf(ParamInfoInput, required=True)
    solution_title = String(required=True)


class DatasetCreate(CustomMutation):
    dataset = Field(DatasetType)

    class Arguments:
        input = DatasetCreateInput(required=True)

    @classmethod
    def mutate(cls, root, info, input: DatasetCreateInput):
        dataset = Dataset.create_dataset(
            title=input.title,
            param_info=input.param_info,
            solution_title=input.solution_title
        )
        print(dataset)
        return DatasetCreate(dataset=dataset)


class Mutations(ObjectType):
    dataset_create = DatasetCreate.Field()

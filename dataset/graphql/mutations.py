from graphene_file_upload.scalars import Upload

from cbr_project_pure.functions import CustomMutation
from cbr_project_pure.graphql_base.base_types import InputObjectType, String, Int, ListOf, Field, ObjectType, ID
from cbr_project_pure.utils import parse_int_param
from dataset.graphql.types import DatasetType
from dataset.models import Dataset
from dataset.services.dataset import DatasetService, DatasetDoesNotExist
from dataset.services.dataset_upload import DatasetUploadService


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


class DatasetValuesUploadInput(InputObjectType):
    dataset_id = ID(required=True)
    file = Upload(required=True)
    csv_delimiter = String()


class DatasetValuesUpload(CustomMutation):
    dataset = Field(DatasetType)

    class Arguments:
        input = DatasetValuesUploadInput(required=True)

    @classmethod
    def mutate(cls, root, info, input: DatasetValuesUploadInput):
        dataset_service = DatasetService()
        dataset = dataset_service.get_from_id(dataset_id=parse_int_param(input.dataset_id))
        if not dataset:
            raise DatasetDoesNotExist(dataset_id=input.dataset_id)

        dataset_upload_service = DatasetUploadService()
        dataset_upload_service.upload_values(
            dataset=dataset,
            file=input.file,
            csv_delimiter=input.csv_delimiter
        )

        return DatasetValuesUpload(dataset=dataset)


class Mutations(ObjectType):
    dataset_create = DatasetCreate.Field()
    dataset_values_upload = DatasetValuesUpload.Field()

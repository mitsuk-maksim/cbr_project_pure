from cbr_project_pure.functions import FieldResolver
from cbr_project_pure.graphql_base.base_types import ObjectType, ID, Argument, NN
from cbr_project_pure.utils import parse_int_param
from dataset.graphql.types import DatasetType, DatasetsQueryListType
from dataset.services.dataset import DatasetService, DatasetDoesNotExist


class DatasetQuery(FieldResolver):
    class Arguments:
        id = Argument(ID, required=True)

    Output = DatasetType

    @staticmethod
    def query(parent, info, id: str):
        dataset_service = DatasetService()
        dataset = dataset_service.get_from_id(dataset_id=parse_int_param(id))
        if not dataset:
            DatasetDoesNotExist(dataset_id=input.id)

        return dataset


class DatasetsQuery(FieldResolver):
    Output = NN(DatasetsQueryListType)

    @staticmethod
    def query(parent, info):
        dataset_service = DatasetService()
        datasets = dataset_service.get_datasets()
        return DatasetsQueryListType(result=datasets)


class Query(ObjectType):
    dataset_query = DatasetQuery.Field()
    datasets_query = DatasetsQuery.Field()

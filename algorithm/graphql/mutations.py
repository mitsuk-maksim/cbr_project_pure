from algorithm.services.knn import KNearestNeighborsService
from cbr_project_pure.functions import CustomMutation
from cbr_project_pure.graphql_base.base_types import InputObjectType, ID, Int, Float, String, Field, ObjectType
from cbr_project_pure.utils import parse_int_param
from dataset.services.dataset import DatasetService, DatasetDoesNotExist
from result.graphql.types import ResultType
from user.permissions import graphql_login_required


class RunAlgorithmKNNInput(InputObjectType):
    dataset_id = ID(required=True)
    k = Int(required=True)
    test_size = Float()
    title = String()


class RunAlgorithmKNN(CustomMutation):
    result = Field(ResultType)

    class Arguments:
        input = RunAlgorithmKNNInput(required=True)

    @classmethod
    @graphql_login_required
    def mutate(cls, root, info, input: RunAlgorithmKNNInput):
        dataset_service = DatasetService()
        dataset = dataset_service.get_from_id(dataset_id=parse_int_param(input.dataset_id))
        if not dataset:
            raise DatasetDoesNotExist(dataset_id=input.dataset_id)
        knn_service = KNearestNeighborsService(user=info.context.user)
        result = knn_service.knn(
            dataset=dataset,
            k=input.k,
            test_size=input.test_size,
            title=input.title
        )
        return RunAlgorithmKNN(result=result)


class Mutations(ObjectType):
    run_algorithm_knn = RunAlgorithmKNN.Field()

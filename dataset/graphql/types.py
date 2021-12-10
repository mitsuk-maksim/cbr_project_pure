from cbr_project_pure.graphql_base.base_types import NN, ObjectType, String, Int, Boolean, ListOf, ID
from dataset.models import Dataset, Parameter


class ParameterType(ObjectType):
    class Meta:
        model = Parameter

    id = NN(ID)
    title = NN(String)
    type = NN(Int)
    description = String()


class DatasetType(ObjectType):
    class Meta:
        model = Dataset

    id = NN(ID)
    title = String()
    public = Boolean()
    parameters = ListOf(ParameterType)

    @staticmethod
    def resolve_parameters(obj: Dataset, info):
        return obj.parameters.all()
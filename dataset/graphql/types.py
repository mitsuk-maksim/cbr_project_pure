from cbr_project_pure.graphql_base.base_types import NN, ObjectType, String, Int, Boolean, ListOf, ID, Enum, Field
from dataset.models import Dataset, Parameter, Solution, SolutionValue, ParameterValue, ParameterTypes
from user.graphql.types import UserType, UserPureType

ParameterEnumType = Enum.from_enum(ParameterTypes)


class SolutionValueType(ObjectType):
    class Meta:
        model = SolutionValue

    id = NN(ID)
    value = NN(String)


class ParameterValueType(ObjectType):
    class Meta:
        model = ParameterValue

    id = NN(ID)
    value = NN(String)


class SolutionType(ObjectType):
    class Meta:
        model = Solution

    id = NN(ID)
    title = NN(String)
    description = String()
    values = ListOf(NN(SolutionValueType))

    @staticmethod
    def resolve_values(obj: Solution, info):
        return obj.solution_values.all()


class ParameterType(ObjectType):
    class Meta:
        model = Parameter

    id = NN(ID)
    title = NN(String)
    type = Field(ParameterEnumType)
    description = String()
    values = ListOf(NN(ParameterValueType))

    @staticmethod
    def resolve_values(obj: Parameter, info):
        return obj.parameter_values.all()


class DatasetType(ObjectType):
    class Meta:
        model = Dataset

    id = NN(ID)
    title = NN(String)
    public = Boolean()
    parameters = ListOf(NN('dataset.graphql.types.ParameterType'))
    solutions = ListOf(NN(SolutionType))
    user = Field(UserPureType)

    @staticmethod
    def resolve_parameters(obj: Dataset, info):
        return obj.parameters.all()

    @staticmethod
    def resolve_solutions(obj: Dataset, info):
        return obj.solutions.all()


class DatasetsQueryListType(ObjectType):
    result = NN(ListOf(NN(DatasetType)))

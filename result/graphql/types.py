from cbr_project_pure.graphql_base.base_types import Enum, ObjectType, NN, ID, Field, String, Float, ListOf
from dataset.graphql.types import DatasetType, ParameterType, ParameterValueType, SolutionValueType
from result.models import ValueType, Result
from user.graphql.types import UserType

ValueEnumType = Enum.from_enum(ValueType)


class ParameterClassType(ObjectType):
    parameter = Field(ParameterType)
    values = ListOf(NN(ParameterValueType))
    type = Field(ValueEnumType)


class ResultType(ObjectType):
    class Meta:
        model = Result

    id = NN(ID)
    user = Field(UserType)
    title = String()
    match_percentage = NN(Float)
    dataset = Field(DatasetType)
    test_parameters = ListOf(NN(ParameterClassType))
    train_parameters = ListOf(NN(ParameterClassType))
    solution_predict_values = ListOf(NN(SolutionValueType))

    @staticmethod
    def resolve_test_parameters(obj: Result, info):
        parameters = obj.dataset.parameters.all()
        result = []
        for parameter in parameters:
            values = obj.parameter_values.filter(parameter=parameter, parametervalueclass__type=ValueType.test).all()
            result.append(ParameterClassType(parameter=parameter, values=values, type=ValueType.test))
        return result

    @staticmethod
    def resolve_train_parameters(obj: Result, info):
        parameters = obj.dataset.parameters.all()
        result = []
        for parameter in parameters:
            values = obj.parameter_values.filter(parameter=parameter, parametervalueclass__type=ValueType.train).all()
            result.append(ParameterClassType(parameter=parameter, values=values, type=ValueType.train))
        return result

    @staticmethod
    def resolve_solution_predict_values(obj: Result, info):
        return obj.solution_predict_values.all()


class ResultQueryListType(ObjectType):
    result = NN(ListOf(ResultType))

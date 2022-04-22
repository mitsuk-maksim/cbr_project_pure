from cbr_project_pure.functions import FieldResolver
from cbr_project_pure.graphql_base.base_types import ID, Argument, ObjectType, NN
from result.graphql.types import ResultType, ResultQueryListType
from result.models import Result
from user.permissions import graphql_login_required


class ResultQuery(FieldResolver):
    class Arguments:
        id = Argument(ID, required=True)

    Output = ResultType

    @staticmethod
    @graphql_login_required
    def query(parent, info, id: str):
        result = Result.objects.filter(id=id).first()
        return result


class ResultsQuery(FieldResolver):
    Output = NN(ResultQueryListType)

    @staticmethod
    @graphql_login_required
    def query(parent, info):
        results = Result.objects.all()
        return ResultQueryListType(result=results)


class Query(ObjectType):
    result_query = ResultQuery.Field()
    results_query = ResultsQuery.Field()

from .base_types import String, Int, DateTime, InputObjectType


class BasePureQueryFilter(InputObjectType):
    query = String()


class BasePureQueryPagination(InputObjectType):
    page = Int(required=True)
    page_size = Int(required=True)


class DateRange(InputObjectType):
    date_from = DateTime(required=True)
    date_to = DateTime(required=True)

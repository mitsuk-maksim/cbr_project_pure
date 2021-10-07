from collections import OrderedDict

import stackprinter
from django.shortcuts import render
from graphene_file_upload.django import FileUploadGraphQLView
from graphql import format_error
from graphql.error import format_error as format_graphql_error
from graphql_jwt import exceptions
from sentry_sdk import capture_exception

from cbr_project_pure.functions import field_from_graphql_message


class CustomGraphQLView(FileUploadGraphQLView):

    def render_graphiql(self, request, **data):
        return render(request, 'graphiql.html', dict(
            GRAPHIQL_VERSION='0.10.2',
            SUBSCRIPTIONS_TRANSPORT_VERSION='0.7.0',
            # subscriptionsEndpoint=SUBSCRIPTION_URL,
            # endpointURL='/graphql/',
        ))

    def execution_result_to_dict(self, execution_result):
        result = OrderedDict()
        if not execution_result:
            return result
        if execution_result.data:
            result['data'] = execution_result.data
        if execution_result and execution_result.errors:
            errors = []
            for error in execution_result.errors:
                if type(getattr(error, 'original_error', None)) == exceptions.PermissionDenied:
                    continue
                data = format_error(error)
                sep_vars = "%s%s" % ((' ') * 4, ('.' * 50))
                data['trace'] = stackprinter.format(error).split(sep_vars)
                errors.append(data)
                capture_exception(error)
            result['errors'] = errors
        return result

    def execute_graphql_request(self, *args, **kwargs):
        """ Extract any exceptions and send them to Sentry """
        result = super().execute_graphql_request(*args, **kwargs)
        self.execution_result_to_dict(result)
        return result

    @staticmethod
    def format_error(error):
        # if isinstance(error, GraphQLError):
        error_format = format_graphql_error(error)
        try:
            message = error.message
        except AttributeError:
            message = error_format.get('message')
        field, error_type = field_from_graphql_message(message)
        error_format.update(dict(field=field))
        return error_format
        # return {"message": six.text_type(error)}
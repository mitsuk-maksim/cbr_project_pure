from cbr_project_pure.functions import graphql_permission

graphql_login_required = graphql_permission(lambda u, *args, **kwargs: not u.is_anonymous)
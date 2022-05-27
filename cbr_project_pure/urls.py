from django.contrib import admin
from django.urls import path
from django.views.decorators.csrf import csrf_exempt
from graphene_django.views import GraphQLView
from graphene_file_upload.django import FileUploadGraphQLView

urlpatterns = [
    path('api/admin/', admin.site.urls),
    # path("graphql/", csrf_exempt(GraphQLView.as_view(graphiql=True))),
    path("api/graphql/", csrf_exempt(FileUploadGraphQLView.as_view(graphiql=True)))
]

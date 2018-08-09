from django.contrib import admin
from django.urls import path
from django.views.decorators.csrf import csrf_exempt

from graphene_django.views import GraphQLView

from core.gql_schema import schema, private_schema
from core.views import PrivateGraphQLView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('graphql/', csrf_exempt(GraphQLView.as_view(graphiql=True, schema=schema))),
    path('private_graphql/', PrivateGraphQLView.as_view(graphiql=True, schema=private_schema)),
]

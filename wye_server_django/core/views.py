from django.http import HttpResponse

from graphene_django.views import GraphQLView


class AuthenticationRequiredMixin(object):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return HttpResponse('Unauthorized', status=401)
        return super().dispatch(request, *args, **kwargs)


class PrivateGraphQLView(AuthenticationRequiredMixin, GraphQLView):
    pass

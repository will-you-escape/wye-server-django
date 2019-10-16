from django.contrib.auth import authenticate, login, logout, get_user_model

import graphene
from graphene_django import DjangoObjectType


class UserType(DjangoObjectType):
    class Meta:
        model = get_user_model()


class Query(graphene.ObjectType):
    whoami = graphene.String(name=graphene.String(default_value="stranger"))

    def resolve_whoami(self, info, name):
        return "I am " + info.context.user.email


class CreateUser(graphene.Mutation):
    user = graphene.Field(UserType)

    class Arguments:
        email = graphene.String(required=True)
        pseudo = graphene.String(required=True)
        password = graphene.String(required=True)

    def mutate(self, info, email, pseudo, password):
        user = get_user_model()(email=email, pseudo=pseudo)
        user.set_password(password)
        user.save()
        login(info.context, user)

        return CreateUser(user=user)


class LoginUser(graphene.Mutation):
    user = graphene.Field(UserType)

    class Arguments:
        email = graphene.String(required=True)
        password = graphene.String(required=True)

    def mutate(self, info, email, password):
        user = authenticate(info.context, email=email, password=password)
        if user is not None:
            login(info.context, user)

        return LoginUser(user=user)


class LogOutUser(graphene.Mutation):
    user = graphene.Field(UserType)

    def mutate(self, info):
        user = info.context.user
        if user and user.is_authenticated:
            logout(info.context)

        return None


class Mutation(graphene.ObjectType):
    create_user = CreateUser.Field()
    login_user = LoginUser.Field()


class PrivateMutation(graphene.ObjectType):
    logout_user = LogOutUser.Field()

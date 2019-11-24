import datetime

from django.contrib.auth import authenticate, login, logout, get_user_model

import graphene
from graphene_django import DjangoObjectType

from rooms.models import EscapeRoomSession


class UserType(DjangoObjectType):
    class Meta:
        model = get_user_model()


class EscapeRoomSessionType(DjangoObjectType):
    def resolve_duration_time(self, info):
        return self.duration_time.total_seconds()

    class Meta:
        model = EscapeRoomSession


class Query(graphene.ObjectType):
    whoami = graphene.String(name=graphene.String(default_value="stranger"))
    room_sessions = graphene.List(EscapeRoomSessionType)

    def resolve_whoami(self, info, name):
        return "I am " + info.context.user.email

    def resolve_room_sessions(self, info):
        return EscapeRoomSession.objects.filter(user=info.context.user)


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


class CreateRoomSession(graphene.Mutation):
    room_session = graphene.Field(EscapeRoomSessionType)

    class Arguments:
        name = graphene.String(required=True)
        played_datetime = graphene.DateTime(required=True)
        duration_time = graphene.Float(required=True)
        number_of_hints = graphene.Int(required=True)

    def mutate(self, info, name, played_datetime, duration_time, number_of_hints):
        formatted_duration_time = datetime.timedelta(seconds=duration_time)

        room_session = EscapeRoomSession.objects.create(
            name=name,
            played_datetime=played_datetime,
            duration_time=formatted_duration_time,
            number_of_hints=number_of_hints,
            user=info.context.user,
        )

        return CreateRoomSession(room_session=room_session)


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
    create_room_session = CreateRoomSession.Field()

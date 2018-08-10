from graphene_django import DjangoObjectType
import graphene

from account.gql_schema import Query, Mutation, PrivateMutation

schema = graphene.Schema(mutation=Mutation)
private_schema = graphene.Schema(query=Query, mutation=PrivateMutation)

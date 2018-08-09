from graphene_django import DjangoObjectType
import graphene

from account.gql_schema import Mutation, PrivateMutation

schema = graphene.Schema(mutation=Mutation)
private_schema = graphene.Schema(mutation=PrivateMutation)

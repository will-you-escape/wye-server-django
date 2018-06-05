from graphene_django import DjangoObjectType
import graphene

from account.gql_schema import Mutation

schema = graphene.Schema(mutation=Mutation)

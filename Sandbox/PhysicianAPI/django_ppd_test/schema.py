import graphene
import django_ppd_test.graphqltest.schema
#Test
class Query(django_ppd_test.graphqltest.schema.Query, graphene.ObjectType):
    pass

class Mutation(django_ppd_test.graphqltest.schema.Mutation, graphene.ObjectType):
    pass

schema = graphene.Schema(query=Query, mutation=Mutation)


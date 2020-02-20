import graphene
from graphene_django.types import DjangoObjectType, ObjectType
from django_ppd_test.graphqltest.models import DjangoTest
from graphene_django.filter import DjangoFilterConnectionField
from graphene import Node, relay

class PhysicianType(DjangoObjectType):
    class Meta:
        model = DjangoTest
        filter_fields = ["me", "first_name", "polo_state"]
        interfaces = (relay.Node, )

class Query(ObjectType):
    #physician = graphene.Field(PhysicianType, me=graphene.Int())
    #allphysicians = graphene.List(PhysicianType)
    #physicians = graphene.List(PhysicianType, mes=graphene.List(graphene.Int))
    physician = relay.Node.Field(PhysicianType)
    physicians = DjangoFilterConnectionField(PhysicianType)
    physicianbyme = graphene.List(PhysicianType, mes=graphene.List(graphene.Int))
    '''
    def resolve_physician(self, info, **kwargs):
        me = kwargs.get('me')
        
        if me is not None:
            return DjangoTest.objects.get(pk=me)

        return None
    '''
    def resolve_allphysicians(self, info, **kwargs):
        return DjangoTest.objects.all()

    
    def resolve_physicianbyme(self, info, **kwargs):
        mes = kwargs.get('mes')
        if mes is not None:
            return [DjangoTest.objects.get(pk=me) for me in mes]

        first_names = kwargs.get("firstName")
        if first_names is not None:
            return [DjangoTest.objects.filter(first_name=first).all() for first in first_names]
        return [] 
 
        
class PhysicianInput(graphene.InputObjectType):
    me = graphene.ID()

class CreatePhysician(graphene.Mutation):
    class Arguments:
        input = PhysicianInput(required=True)
    
    ok = graphene.Boolean()
    physician = graphene.Field(PhysicianType)

    @staticmethod
    def mutate(root, info, input=None):
        ok = True
        physician_instance = DjangoTest(me=input.me)
        return CreatePhysician(ok=ok, actor=physician_instance)

class Mutation(graphene.ObjectType):
    create_physician = CreatePhysician.Field()

schema = graphene.Schema(query=Query, mutation=Mutation)

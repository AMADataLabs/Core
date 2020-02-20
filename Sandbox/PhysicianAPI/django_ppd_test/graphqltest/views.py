from django.shortcuts import render
from django_ppd_test.graphqltest.models import DjangoTest
from django_ppd_test.graphqltest.serializers import PhysicianSerializer
from rest_framework import generics
from django_filters.rest_framework import DjangoFilterBackend
import inspect

#Learn more or give us feedback
from rest_framework.response import Response
from rest_framework.views import status

# Create your views here.


class PhysicianList(generics.ListAPIView):
    queryset = DjangoTest.objects.all()
    serializer_class = PhysicianSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = '__all__'

    def list(self, request, *args, **kwargs):
        """
        Override the method from the parent class. We just now get the parameter 
        fields and pass these fields to the serializer so the client can control what they get.
        """
        queryset = self.filter_queryset(self.get_queryset())
        fields = request.query_params.get('fields')
        if fields is not None:
            fields = [str(item) for item in fields.split(',')]
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True, fields=fields)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True, fields=fields)
        return Response(serializer.data)

class PhysiciansDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = DjangoTest.objects.all()
    serializer_class = PhysicianSerializer

    def get(self, request, *args, **kwargs):
        try:
            a_physician = self.queryset.get(pk=kwargs["pk"])
            fields = request.query_params.get('fields')
            if fields is not None:
                fields = [str(item) for item in fields.split(',')]
            return Response(PhysicianSerializer(a_physician, fields=fields).data)
        except DjangoTest.DoesNotExist:
            return Response(
                data={
                    "message": "Physician with id: {} does not exist".format(kwargs["pk"])
                },
                status=status.HTTP_404_NOT_FOUND
            )


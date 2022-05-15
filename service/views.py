from django.http import Http404
from django.db.models import Q, Prefetch, Count
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication

from .models import Category, Services, Parameters
from . import serializers as srl
from utils.permitions import HasGroupPermission


class CategoryView(APIView):
    permission_classes = (IsAuthenticated, HasGroupPermission)
    authentication_classes = (TokenAuthentication,)
    required_groups = {
        'GET': ['reception'],
        'POST': []
    }

    def get(self, request):
        query = request.GET.get('search')
        if query is not None:
            category = Category.objects.all().prefetch_related(
                Prefetch('service',
                         queryset=Services.objects.filter(
                             Q(name__icontains=query.lower()) |
                             Q(name__icontains=query.title()) |
                             Q(name__icontains=query.upper())
                            )
                         )
            )
            # Q(Q(service__name__icontains=query.lower()) |
            #   Q(service__name__icontains=query.title()) |
            #   Q(service__name__icontains=query.upper()))
            temp = []
            for i in category:
                if i.service.count():
                    temp.append(i)
            category = temp
        else:
            category = Category.objects.all().prefetch_related('service')
        serializer = srl.CategoryAndServiceGet(category, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = srl.CategoryPOST(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(data=serializer.data, status=status.HTTP_201_CREATED)
        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CategoryDetailView(APIView):
    permission_classes = (IsAuthenticated, HasGroupPermission)
    authentication_classes = (TokenAuthentication,)
    required_groups = {
        'GET': ['reception'],
        'PUT': [],
        'DELETE': []
    }

    def get_data(self, pk):
        try:
            data = Category.objects.get(pk=pk)
            return data
        except ObjectDoesNotExist:
            raise Http404("Data not found!!!")

    def get(self, request, pk):
        category = self.get_data(pk=pk)
        serializer = srl.CategoryGET(category)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        category = self.get_data(pk=pk)
        serializer = srl.CategoryPOST(category, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"request": "your data is updated"},
                            status=status.HTTP_200_OK)

        return Response({"request": "your data is not updated",
                         "error": serializer.errors},
                        status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        category = self.get_data(pk=pk)
        try:
            category.delete()
            return Response(data={'request': 'Data successfully deleted'}, status=status.HTTP_204_NO_CONTENT)
        except Exception:
            return Response(data={'request': 'Oops Something went wrong'}, status=status.HTTP_400_BAD_REQUEST)


class ParameterView(APIView):
    permission_classes = (IsAuthenticated, HasGroupPermission)
    authentication_classes = (TokenAuthentication,)
    required_groups = {
        'GET': ['laboratory1', 'laboratory2'],
        'POST': []
    }

    def get(self, request):
        param_obj = Parameters.objects.all()
        serializer = srl.ParameterSerializerGet(param_obj, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = srl.ParameterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(data=serializer.data, status=status.HTTP_201_CREATED)
        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ParameterDetailView(APIView):
    permission_classes = (IsAuthenticated, HasGroupPermission)
    authentication_classes = (TokenAuthentication,)
    required_groups = {
        'GET': ['laboratory1', 'laboratory2'],
        'PUT': [],
        'DELETE': []
    }

    def get_data(self, pk):
        try:
            data = Parameters.objects.get(pk=pk)
            return data
        except ObjectDoesNotExist:
            raise Http404("Service not found!!!")

    def get(self, request, pk):
        parameter = self.get_data(pk=pk)
        serializer = srl.ParameterSerializerGet(parameter)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        parameter = self.get_data(pk=pk)
        serializer = srl.ParameterSerializer(parameter, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        parameter = self.get_data(pk=pk)
        try:
            parameter.delete()
            return Response(data={'request': 'Data successfully deleted'}, status=status.HTTP_204_NO_CONTENT)
        except Exception:
            return Response(data={'request': 'Oops Something went wrong'}, status=status.HTTP_400_BAD_REQUEST)


class ServiceView(APIView):
    permission_classes = (IsAuthenticated, HasGroupPermission)
    authentication_classes = (TokenAuthentication,)
    required_groups = {
        'GET': ['laboratory1', 'laboratory2', 'reception'],
        'POST': []
    }

    def get(self, request):
        service = Services.objects.select_related('category_id')
        serializer = srl.ServiceGet(service, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = srl.ServicePost(data=request.data)
        if serializer.is_valid():
            serializer.save()
            service = Services.objects.get(pk=serializer.data['id'])
            for i in request.data['parameters']:
                param_obj = Parameters.objects.get(pk=i)
                service.parameters.add(param_obj)
            serializer = srl.ServicePost(service)
            return Response(data=serializer.data, status=status.HTTP_201_CREATED)
        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ServiceDetailView(APIView):
    permission_classes = (IsAuthenticated, HasGroupPermission)
    authentication_classes = (TokenAuthentication,)
    required_groups = {
        'GET': ['laboratory1', 'laboratory2', 'reception'],
        'PUT': [],
        'DELETE': []
    }

    def get_data(self, pk):
        try:
            data = Services.objects.get(pk=pk)
            return data
        except ObjectDoesNotExist:
            raise Http404("Service not found!!!")

    def get(self, request, pk):
        service = self.get_data(pk=pk)
        serializer = srl.ServiceGet(service)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        service = self.get_data(pk=pk)
        serializer = srl.ServicePost(service, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        service = self.get_data(pk=pk)
        try:
            service.delete()
            return Response(data={'request': 'Data successfully deleted'}, status=status.HTTP_204_NO_CONTENT)
        except Exception:
            return Response(data={'request': 'Oops Something went wrong'}, status=status.HTTP_400_BAD_REQUEST)



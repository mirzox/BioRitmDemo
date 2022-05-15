from datetime import datetime
from django.http import Http404
from django.core.exceptions import ObjectDoesNotExist
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework import filters
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication

from .models import Order, ParamResult, Result
from . import serializers as srl
from service.models import Services
from client.models import Patient
from service.serializers import ServiceGet
from account.models import ChoiceCategories
from utils.checkout import i_path, GenerateXlsx, i_path2
from utils.permitions import HasGroupPermission
from utils.pagination import PaginationHandlerMixin, BasicPagination
from utils.mergepdfs import merge


class OrderView(ListAPIView, APIView, PaginationHandlerMixin):
    permission_classes = (IsAuthenticated, HasGroupPermission)
    authentication_classes = (TokenAuthentication,)
    pagination_class = BasicPagination
    # queryset = Order.objects.all().select_related('patient_id').prefetch_related('services').order_by("-timestamp")
    serializer_class = srl.OrderGet
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    filterset_fields = ['status', ]
    search_fields = ['^id', 'patient_id__firstname', 'patient_id__phone', 'patient_id__secondname',
                     'doctor_id__firstname', 'doctor_id__id', 'timestamp']
    required_groups = {
        'GET': ['laboratory1', 'laboratory2', 'reception'],
        'POST': ['reception']
    }
    role = ''
    categories = []

    def get_queryset(self):
        if self.request.user.is_staff or self.request.user.is_superuser:
            queryset = Order.objects.all().select_related('patient_id').prefetch_related('services').order_by(
                "-timestamp")

        elif self.role == "laboratory1":
            queryset = Order.objects.filter(
                services__in=Services.objects.filter(
                    category_id__in=ChoiceCategories.objects.get(user_id=self.request.user).categories.all()
                )
            ).select_related('patient_id').prefetch_related('services').order_by(
                "-timestamp").distinct()

            # services = Services.objects.filter(
            #     category_id__in=ChoiceCategories.objects.get(user_id=self.request.user).categories.all()
            # )
            # print(services)
            # print(ChoiceCategories.objects.get(user_id=self.request.user).categories.all())
            # queryset = queryset.filter(
            #     services__in=services
            # )
        # order_status = self.request.query_params.get("status")
        # search = self.request.query_params.get("search")

        return queryset

    # def get(self, request):
    #     order = Order.objects.all().
    #     serializer = srl.OrderGet(order, many=True)
    #     return Response(data=serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        try:
            request.data._mutable = True
        except AttributeError:
            pass
        patient = Patient.objects.get(pk=request.data['patient_id']).doctor_id
        if patient is not None:
            request.data['doctor_id'] = patient.id
        serializer = srl.OrderPost(data=request.data)
        if serializer.is_valid():
            serializer.save()
            order = Order.objects.get(pk=serializer.data['id'])
            cost = 0
            for i in request.data['services']:
                service_obj = Services.objects.filter(pk=i).select_related("category_id").prefetch_related('parameters')[0]

                cost += service_obj.price
                order.services.add(service_obj)
                # if service_obj.category_id.name not in ["УЗИ", "Консультации Врачей", "Услуги Гинеколога"]:
                if service_obj.category_id.is_continuous:
                    result = Result.objects.create(service_id=service_obj, patient_id_id=order.patient_id_id)
                    serv_ser = ServiceGet(service_obj).data
                    for j in serv_ser['parameters']:
                        param_result = ParamResult.objects.create(param_id_id=j['id'])
                        result.result.add(param_result)
                    order.results.add(result)
            Check = GenerateXlsx(input_path=i_path)
            data = Services.objects.filter(pk__in=request.data['services']).values_list('name', 'price')
            full_name = f"{request.user.first_name}"
            o_path = Check.main(rec_name=full_name, data=data)
            order.file = f"{o_path.replace('mediafiles', 'media')}"
            p_file_o = Check.check_for_patient(i_path=i_path2, rec_name=full_name,
                                               pat_name=order.patient_id.firstname, data=data)
            order.cost = cost
            order.p_file = f"{p_file_o.replace('mediafiles', 'media')}"
            order.save()
            serializer = srl.OrderPost(order)
            if order.results.all().count() == 0:
                order.status = "finished"
                order.save()
            return Response(data=serializer.data, status=status.HTTP_201_CREATED)
        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# class GetDocument(APIView):
#     permission_classes = (IsAuthenticated, HasGroupPermission)
#     authentication_classes = (TokenAuthentication,)
#     required_groups = {
#         'GET': ['reception'],
#     }
#
#     def get(self, request):
#         id = request.data.get('id', 0)
#         if id:
#             pass


class ResultView(ListAPIView, PaginationHandlerMixin, APIView):
    permission_classes = (IsAuthenticated, HasGroupPermission)
    authentication_classes = (TokenAuthentication,)
    pagination_class = BasicPagination
    queryset = Order.objects.all().select_related('patient_id').order_by("-id")
    serializer_class = srl.Temp2
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    filterset_fields = ['status']
    search_fields = ['^id', 'patient_id__firstname', 'patient_id__phone', 'patient_id__secondname',
                     'doctor_id__firstname', 'doctor_id__id', 'timestamp', 'services__name',
                     'services__category_id__name']
    required_groups = {
        'GET': ['laboratory1', 'laboratory2']
    }


class ResultsDetailView(APIView):
    permission_classes = (IsAuthenticated, HasGroupPermission)
    authentication_classes = (TokenAuthentication,)

    required_groups = {
        'GET': ['laboratory1', 'laboratory2'],
        'PUT': ['laboratory1', 'laboratory2']
    }

    def get(self, request, pk):
        # try:
        order = Order.objects.filter(pk=pk).select_related('patient_id')
        if len(order) == 0:
            raise Http404("Order not found!!!")
        serializer = srl.Temp2(order[0])
        return Response(data=serializer.data, status=status.HTTP_200_OK)
        # except ObjectDoesNotExist:
        #     raise Http404("Order not found!!!")

    def put(self, request, pk):
        data = request.data.get("results", False)
        if data:
            for i in data:
                if ParamResult.objects.get(pk=i["id"]).result_set.all()[0].order_set.all()[0].id == pk:
                    param = ParamResult.objects.filter(pk=i["id"]).update(res=i['res'])
            param = ParamResult.objects.get(pk=i['id'])
            param.save()
            order = Order.objects.filter(pk=pk).select_related('patient_id')
            serializer = srl.Temp2(order, many=True)
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        return Response(data={"error": "something went wrong"}, status=status.HTTP_400_BAD_REQUEST)


class OrderFilesView(APIView):
    permission_classes = (IsAuthenticated, HasGroupPermission)
    authentication_classes = (TokenAuthentication,)

    required_groups = {
        'GET': ['laboratory1', 'laboratory2']
    }

    def get(self, request):
        order_ids = request.data.get("files", False)
        if order_ids:
            file_names = Order.objects.filter(pk__in=order_ids).values_list("result_file", flat=True)
            file = merge(file_names)
            return Response(data={"request": "file ok", "file": file}, status=status.HTTP_200_OK)
        # else:
        start = datetime.today()
        file_names = Order.objects.filter(
                timestamp__day=start.day,
                timestamp__month=start.month,
                timestamp__year=start.year,
                result_file__isnull=False).values_list("result_file", flat=True)
        if len(file_names):
            file = merge(file_names)
            return Response(data={"request": "file ok", "file": file}, status=status.HTTP_200_OK)
        return Response(data={"request": "Orders not found"}, status=status.HTTP_400_BAD_REQUEST)

from random import randint
from datetime import datetime, timedelta

from django.http import Http404
from django.db.models import Q
from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework import filters
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.authentication import TokenAuthentication

from .models import Doctor, Patient
from . import serializers as srl
from utils.permitions import HasGroupPermission
from utils.pagination import PaginationHandlerMixin, BasicPagination
# from utils.smsservice import Sms


class DoctorView(ListAPIView, APIView, PaginationHandlerMixin):
    permission_classes = (IsAuthenticated, IsAdminUser)
    authentication_classes = (TokenAuthentication,)
    pagination_class = BasicPagination
    queryset = Doctor.objects.all()
    serializer_class = srl.DoctorGetSerializer
    filter_backends = [filters.SearchFilter, ]
    search_fields = ['^id', 'firstname', 'secondname', 'phone', 'location', 'timestamp']

    def post(self, request):
        serializer = srl.DoctorPostSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(data=serializer.data, status=status.HTTP_201_CREATED)
        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#
# class DoctorView(APIView):
#     permission_classes = (IsAuthenticated, IsAdminUser)
#     authentication_classes = (TokenAuthentication,)
#
#     def get(self, request):
#         query = request.GET.get('search')
#         doctors = Doctor.objects.all()
#         if query:
#             doctor = doctors.filter(
#                 Q(firstname__icontains=query) |
#                 Q(secondname__icontains=query) |
#                 Q(phone__icontains=query) |
#                 Q(location__icontains=query)
#             )
#             serializer = srl.DoctorGetSerializer(doctor, many=True)
#         else:
#             serializer = srl.DoctorGetSerializer(doctors, many=True)
#         return Response(data=serializer.data, status=status.HTTP_200_OK)
#
#     def post(self, request):
#         serializer = srl.DoctorPostSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(data=serializer.data, status=status.HTTP_201_CREATED)
#         return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DoctorDetailView(APIView):
    permission_classes = (IsAuthenticated, IsAdminUser)
    authentication_classes = (TokenAuthentication, )

    def get_data(self, pk: int):
        try:
            return Doctor.objects.get(pk=pk)
        except ObjectDoesNotExist:
            raise Http404("Data not found!!!")

    def get(self, request, pk):
        serializer = srl.DoctorGetSerializer(self.get_data(pk=pk))
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        serializer = srl.DoctorPostSerializer(self.get_data(pk=pk), data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"request": "your data is updated"},
                            status=status.HTTP_200_OK)

        return Response({"request": "your data is not updated",
                         "error": serializer.errors},
                        status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        doctor = self.get_data(pk=pk)
        try:
            doctor.delete()
            return Response(data={'request': 'Data successfully deleted'}, status=status.HTTP_204_NO_CONTENT)
        except Exception:
            return Response(data={'request': 'Oops Something went wrong'}, status=status.HTTP_400_BAD_REQUEST)


class PatientView(ListAPIView, APIView, PaginationHandlerMixin):
    permission_classes = (IsAuthenticated, HasGroupPermission)
    authentication_classes = (TokenAuthentication, )
    pagination_class = BasicPagination
    queryset = Patient.objects.all()
    serializer_class = srl.PatientGetSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['gender', "order_status"]
    search_fields = ['firstname', 'secondname', 'phone', "order_status"]
    required_groups = {
        'GET': ['reception'],
        'POST': ['reception']
    }

    def get_queryset(self):
        queryset = Patient.objects.all()
        days = self.request.query_params.get('date', 'all')
        if days == 'yesterday':
            start = datetime.today() - timedelta(1)
            queryset = queryset.filter(
                timestamp__day=start.day,
                timestamp__month=start.month,
                timestamp__year=start.year
            )
        elif days == 'today':
            start = datetime.today()
            queryset = queryset.filter(
                timestamp__day=start.day,
                timestamp__month=start.month,
                timestamp__year=start.year
            )
        return queryset

    def post(self, request):
        serializer = srl.PatientPostSerializer(data=request.data)
        doctor_id = request.data.get("doctor_id")
        if doctor_id is not None:
            doctor, created = Doctor.objects.get_or_create(pk=doctor_id)
        if serializer.is_valid():
            serializer.save()
            return Response(data=serializer.data, status=status.HTTP_201_CREATED)
        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PatientDetailView(APIView):
    permission_classes = (IsAuthenticated, HasGroupPermission)
    authentication_classes = (TokenAuthentication, )
    required_groups = {
        'GET': ['reception'],
        'PUT': ['reception'],
        'DELETE': []
    }

    def get_data(self, pk: int):
        try:
            return Patient.objects.get(pk=pk)
        except ObjectDoesNotExist:
            raise Http404("Data not found!!!")

    def get(self, request, pk):
        serializer = srl.PatientGetSerializer(self.get_data(pk=pk))
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        serializer = srl.PatientPostSerializer(self.get_data(pk=pk), data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"request": "your data is updated"},
                            status=status.HTTP_200_OK)

        return Response({"request": "your data is not updated",
                         "error": serializer.errors},
                        status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        patient = self.get_data(pk=pk)
        try:
            patient.delete()
            return Response(data={'request': 'Data successfully deleted'}, status=status.HTTP_204_NO_CONTENT)
        except Exception:
            return Response(data={'request': 'Oops Something went wrong'}, status=status.HTTP_400_BAD_REQUEST)


# class VerifyPhoneView(APIView):
#     permission_classes = (IsAuthenticated, HasGroupPermission)
#     authentication_classes = (TokenAuthentication,)
#     required_groups = {
#         'POST': ['reception']
#     }
#
#     def post(self, request):
#         phone = srl.PhoneSerializer(data=request.data)
#         phone.is_valid(raise_exception=True)
#         phone = phone.data['phone']
#         code = cache.get(phone)
#         if code:
#             cache.set(f"{phone}", code, timeout=240)
#             data = Sms.send_sms(phone=phone, message=f"Your verification code: {code}")
#             # if not ok:
#             #     return Response(data=data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
#             return Response(data=data, status=status.HTTP_201_CREATED)
#         code = randint(1000, 9999)
#         cache.set(f"{phone}", code, timeout=300)
#         data = Sms.send_sms(phone=phone, message=f"Your verification code: {code}")
#         # if not ok:
#         #     return Response(data=data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
#         return Response(data=data, status=status.HTTP_201_CREATED)
#
#
# class ConfirmPhone(APIView):
#     permission_classes = (IsAuthenticated, HasGroupPermission)
#     authentication_classes = (TokenAuthentication,)
#     required_groups = {
#         'POST': ['reception']
#     }
#
#     def post(self, request):
#         phone = request.data.get('phone')
#         code = cache.get(phone, 1)
#         print(code)
#         if int(code) == int(request.data.get('code')) and code is not None:
#             cache.expire(f"{phone}", timeout=1)
#             return Response(data={"request": "Phone successfully confirmed"}, status=status.HTTP_200_OK)
#         return Response(data={"request": "Invalid code"}, status=status.HTTP_400_BAD_REQUEST)

from datetime import datetime, timedelta
import os
import shutil
from zipfile import ZipFile

from django.conf import settings
from django.http import Http404
from django.core.exceptions import ObjectDoesNotExist
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework import filters
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.authentication import TokenAuthentication
from django.db.models import Count, F, Sum, Q

from utils.permitions import HasGroupPermission
from order.models import Order
from .serializers import OrderSerializer
from utils.xls import ExcelSheet


class FeeView(APIView):
    permission_classes = (IsAuthenticated, IsAdminUser)
    authentication_classes = (TokenAuthentication,)

    def get(self, request):
        end = request.GET.get("end")
        if end is not None:
            end = datetime.date(datetime.strptime(end, "%Y-%m-%d"))
        else:
            end = datetime.date(datetime.today())
        try:
            start = datetime.date(datetime.strptime(request.GET.get("start",
                                                                    end - timedelta(request.GET.get('days', 1))),
                                                    "%Y-%m-%d"))
        except Exception:
            raise Http404()

        result = {}
        order = Order.objects.filter(
            doctor_id__isnull=False, timestamp__gte=start, timestamp__lte=end).select_related("patient_id")
        doctors = list(set(order.values_list("doctor_id", flat=True).order_by("doctor_id")))

        doctors.sort()
        for i in doctors:
            result[i] = OrderSerializer(order.filter(doctor_id=i), many=True).data
        if len(result) != 0:
            file_name = 'mediafiles/fee/{}_{}.xlsx'.format(start, end)
            output_path = os.path.join(settings.BASE_DIR, file_name)
            temp = ExcelSheet(output_path)
            temp.fill_the_sheet(result)
            temp.save()
            return Response(data={"file": f"/{file_name.replace('mediafiles', 'media')}"}, status=status.HTTP_200_OK)
        return Response(data={}, status=status.HTTP_400_BAD_REQUEST)


class DataView(APIView):
    permission_classes = (IsAuthenticated, IsAdminUser)
    authentication_classes = (TokenAuthentication,)

    def get(self, request):
        order = Order.objects.all().annotate(time=F('timestamp__date')).values("time").annotate(items=Count('id'),
                                                                                                cost=Sum("cost"))
        total, used, free = shutil.disk_usage("/")
        data = {
            "storage": {
                "total": total // 2**20,
                "used": used // 2**20,
                "free": free // 2**20
            },
            "files": sorted([f"/media/fee/{i}" for i in os.listdir(os.path.join(settings.BASE_DIR, 'mediafiles/fee'))]),
            "order": list(order)
        }
        return Response(data=data, status=status.HTTP_200_OK)


class DataDetailView(APIView):
    permission_classes = (IsAuthenticated, IsAdminUser)
    authentication_classes = (TokenAuthentication,)

    def delete(self, request, file):
        try:
            file_path = os.path.join(settings.BASE_DIR, f"mediafiles/fee/{file}")
            os.remove(file_path)
            return Response({"request": "file successfully deleted"}, status=status.HTTP_204_NO_CONTENT)
        except Exception:
            return Response({}, status=status.HTTP_400_BAD_REQUEST)


class ZipAll(APIView):
    permission_classes = (IsAuthenticated, IsAdminUser)
    authentication_classes = (TokenAuthentication,)

    def get(self, request):
        filename_ = datetime.date(datetime.today())
        o_path = os.path.join(settings.BASE_DIR, f"mediafiles/zipfiles/{filename_}.zip")
        with ZipFile(o_path, 'w') as zipObj:
            for folderName, subfolders, filenames in os.walk(os.path.join(settings.BASE_DIR, 'mediafiles/')):
                if folderName.split('/')[-1] in ["kassa", "fee", "mergedresults", "results"]:
                    for filename in filenames:
                        # create complete filepath of file in directory
                        filePath = os.path.join(folderName, filename)
                        # Add file to zip
                        zipObj.write(filePath, f"{folderName.split('/')[-1]}/{os.path.basename(filePath)}")
        return Response({"data": f"/api/media/zipfiles/{filename_}.zip"}, status=status.HTTP_200_OK)

    def delete(self, request):
        try:
            # file_path = os.path.join(settings.BASE_DIR, f"mediafiles/zipfiles/{file}")
            # os.remove(file_path)
            for path in ["kassa", "fee", "mergedresults", "results", "zipfiles"]:
                for i in os.listdir(os.path.join(settings.BASE_DIR, f"mediafiles/{path}/")):
                    os.remove(os.path.join(settings.BASE_DIR, f"mediafiles/{path}/{i}"))
            return Response({"request": "Файлы успешно удалены с сервера"}, status=status.HTTP_204_NO_CONTENT)
        except Exception:
            return Response({}, status=status.HTTP_400_BAD_REQUEST)


# class ZipDetailView(APIView):
#     permission_classes = (IsAuthenticated, IsAdminUser)
#     authentication_classes = (TokenAuthentication,)
#
#     def delete(self, request, file):
#         try:
#             file_path = os.path.join(settings.BASE_DIR, f"mediafiles/zipfiles/{file}")
#             os.remove(file_path)
#             for path in ["kassa", "fee", "mergedresults", "results"]:
#                 for i in os.listdir(os.path.join(settings.BASE_DIR, f"mediafiles/{path}/")):
#                     os.remove(i)
#             return Response({"request": "archive successfully deleted"}, status=status.HTTP_204_NO_CONTENT)
#         except Exception:
#             return Response({}, status=status.HTTP_400_BAD_REQUEST)

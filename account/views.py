from django.http import Http404
from django.shortcuts import redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User, Group
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authentication import TokenAuthentication

from . import serializers as srl
from utils.permitions import HasGroupPermission


class LoginView(ObtainAuthToken):
    # authentication_classes = (TokenAuthentication,)

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        # if not request.user.is_authenticated:
        token, created = Token.objects.get_or_create(user=user)
        data = srl.UserSerializer(User.objects.filter(pk=user.pk).prefetch_related('photo'), many=True)
        if user.is_superuser or user.is_staff:
            role = "admin"
        else:
            try:
                role = Group.objects.get(user=user).name
            except ObjectDoesNotExist:
                role = ''
        return Response({
            'token': token.key,
            'role': role,
            'user_data': data.data[0]
        }, status=status.HTTP_201_CREATED)


class Logout(APIView):
    permission_classes = [IsAuthenticated, ]
    authentication_classes = (TokenAuthentication, )

    def get(self, request, format=None):
        request.user.auth_token.delete()
        return Response({
            'response': 'token successfully deleted'
            }, status=status.HTTP_200_OK
        )


# class ChangePasswordView(APIView):
#     permission_classes = [IsAuthenticated, IsAdminUser]
#     authentication_classes = (TokenAuthentication, )
#
#     def get_data(self, pk):
#         try:
#             data = User.objects.get(pk=pk)
#             return data
#         except ObjectDoesNotExist:
#             raise Http404("User not  found!!!")
#
#     def put(self, request, pk, *args, **kwargs):
#         user = self.get_data(pk=pk)
#
#         serializer = srl.ChangePasswordSerializer(user, data=request.data, context={'request': request})
#         if serializer.is_valid():
#             serializer.save()
#             return Response(data={'request': "password successfully updated!!!"}, status=status.HTTP_200_OK)
#         return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AccountView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]
    authentication_classes = (TokenAuthentication,)

    def get(self, request):
        users = User.objects.filter(is_superuser=False).prefetch_related('photo')
        serializer = srl.UserSerializer(users, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)


class AccountDetailView(APIView):
    permission_classes = [IsAuthenticated, HasGroupPermission]
    authentication_classes = (TokenAuthentication,)

    required_groups = {
        'GET': ["laboratory1", "laboratory2", "reception"],
        'PUT': []
    }

    def get_data(self, pk):
        try:
            data = User.objects.get(pk=pk)
            if data.is_superuser:
                raise Http404("User not  found!!!")
            return data
        except ObjectDoesNotExist:
            raise Http404("User not  found!!!")

    def get(self, request, pk):
        user = self.get_data(pk=pk)
        if not request.user.is_staff:
            if request.user.id != pk:
                return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = srl.UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk, *args, **kwargs):
        context = {"photo": request.data.get('photo'), "new_password": request.data.get("new_password")}
        user = self.get_data(pk=pk)
        serializer = srl.UserSerializer(user, data=request.data, partial=True, context=context)
        if serializer.is_valid():
            serializer.save()
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AutoLogin(APIView):
    permission_classes = [IsAuthenticated, ]
    authentication_classes = (TokenAuthentication,)

    def get(self, request):
        user = User.objects.get(username=request.user.username)
        auser = authenticate(request, username=user.username, password=user.password)
        login(request, auser)
        return Response({"response": "Success"}, status=status.HTTP_200_OK)

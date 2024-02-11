from django.shortcuts import render,get_object_or_404
from rest_framework import viewsets,status
from user.models import User
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.http import Http404
from user.serializer import UserRegistrationSerializer,UserLoginSerializer,UserSerializer,GetUserSerializer
import pdb
# from curiocamp.settings import FACULTY_SECRET_KEY
import jwt
from datetime import datetime, timedelta
from django.conf import settings
from django.contrib.auth import authenticate,login
from rest_framework.decorators import permission_classes,authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import AllowAny

def responsegenerator(status, results=None, message=None, errors=None):
    response_data = {"statusCode": status}
    
    if results is not None:
        response_data["results"] = results

    if message is not None:
        response_data["message"] = message

    if errors is not None:
        response_data["errors"] = errors

    return response_data

def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }
    

class UserRegistrationViewset(viewsets.ModelViewSet):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    http_method_names = ['get', 'post', 'patch', 'head', 'options', 'put']
    serializer_class = UserRegistrationSerializer
    
    def create(self, request, *args, **kwargs):
        data = request.data
        try:
            serializer = UserRegistrationSerializer(data=data)
            if serializer.is_valid():
                saved_serializer = serializer.save()
                api_response = responsegenerator(status=status.HTTP_200_OK, results=serializer.data,message='User Created Successfully')
                api_response['token'] = get_tokens_for_user(saved_serializer)
                return Response(api_response)
            api_response = responsegenerator(status=status.HTTP_400_BAD_REQUEST, errors=serializer.errors)
            return Response(api_response)
        except Exception as e:
            print(e)
            api_response = responsegenerator(status=status.HTTP_500_INTERNAL_SERVER_ERROR, message='Something Went Wrong')
            return Response(api_response)

    def retrieve(self, request, pk=None):
        user = self.get_object()
        serializer = GetUserSerializer(user)
        # return Response(serializer.data)
        api_response = responsegenerator(status=status.HTTP_200_OK,results=serializer.data)
        return Response(api_response)

    def update(self, request, pk=None):
        user = self.get_object()
        serializer = UserSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            api_response = responsegenerator(status=status.HTTP_200_OK, results=serializer.data,message="User Details Updated Successfully")
            return Response(api_response)
        api_response = responsegenerator(status=status.HTTP_400_BAD_REQUEST, errors=serializer.errors)
        return Response(api_response)

class UserLoginViewset(viewsets.ViewSet):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    http_method_names = ['post']
    serializer_class = UserLoginSerializer

    def create(self, request, *args, **kwargs):
        data = request.data
        try:
            email = data.get('email')
            password = data.get('password')
            user = authenticate(email=email,password=password)
            if user is None:
                response = responsegenerator(status=status.HTTP_400_BAD_REQUEST,message="Unable to login, Please check email or password.")
                return Response(response)
            tokens = get_tokens_for_user(user)
            serializer = UserLoginSerializer(user)
            api_response = responsegenerator(status=status.HTTP_200_OK,message='Logged In',)
            api_response['token'] = tokens
            return Response(api_response)
        except Exception as e:
            print(e)
            api_response = responsegenerator(status=status.HTTP_500_INTERNAL_SERVER_ERROR, message='Something Went Wrong')
            return Response(api_response)
        

@api_view(['POST'])
def becomeInstructor(request):
    data = request.data
    try:
        otp = data.get('otp')
        user_id = data.get('user_id')
        if otp == '1234':
            user = User.objects.get(id=user_id)
            user.user_type = 'Instructor'
            user.save()
            api_response = responsegenerator(status=status.HTTP_200_OK,message='Successfully Updated to Instructor')
            return Response(api_response)
        api_response = responsegenerator(status=status.HTTP_400_BAD_REQUEST,message='Invalid OTP')
        return Response(api_response)
    except Exception as e:
        print(e)
        api_response = responsegenerator(status=status.HTTP_500_INTERNAL_SERVER_ERROR, message='Something Went Wrong')
        return Response(api_response)
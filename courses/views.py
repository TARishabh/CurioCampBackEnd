from django.shortcuts import render,get_object_or_404
from rest_framework import viewsets,status
from courses.models import Course,Module,Content,Enrollment,Progress,RazorpayOrder
from user.models import User
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.http import Http404
from courses.serializer import CourseSerializer,ModuleSerializer,ContentSerializer,EnrollmentSerializer,ProgressSerializer,EnrollmentListSerializer,RazorPayOrderSerializer
from datetime import datetime, timedelta
from rest_framework.decorators import permission_classes,authentication_classes
from rest_framework.permissions import IsAuthenticated, BasePermission
from rest_framework.permissions import AllowAny
from rest_framework.pagination import PageNumberPagination
from user.views import responsegenerator
import razorpay
# Create your views here.

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class IsOwnerOrReadOnly(BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return True

        # Write permissions are only allowed to the owner of the course.
        if obj.course.creator == request.user:
            return True
        elif obj.course.creator != request.user:
            return False

        return obj.creator == request.user
    
class IsModuleOwnerOrReadOnly(BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return True

        # Write permissions are only allowed to the owner of the course.
        return obj.module.course.creator == request.user

class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    pagination_class = StandardResultsSetPagination
    
    def get_permissions(self):
        if self.action == 'list':
            # Allow unauthenticated users to list all courses
            return []
        elif self.action in ['create', 'update', 'partial_update', 'destroy']:
            # Allow only authenticated users and admin to perform create, update, and delete actions
            return [IsAuthenticated()]
        else:
            # For all other actions, use IsOwnerOrReadOnly permission
            return [IsOwnerOrReadOnly()]
    def create(self, request, *args, **kwargs):
        try:
            data = request.data
            user_id = data.get('creator')
            
            user_type = User.objects.get(id=user_id)
            if user_type.user_type != 'Instructor':
                api_response = responsegenerator(status=status.HTTP_401_UNAUTHORIZED,message="You Do not Have the Permission.")
                return Response(api_response)
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                serializer.save(creator=request.user)
                # headers = self.get_success_headers(serializer.data)
                api_response = responsegenerator(status=status.HTTP_201_CREATED,results=serializer.data,message="Course Added Successfully.")
                return Response(api_response)
            api_response = responsegenerator(status=status.HTTP_400_BAD_REQUEST,errors=serializer.errors)
            return Response(api_response)
        except Exception as e:
            print(e)
            api_response = responsegenerator(status=status.HTTP_500_INTERNAL_SERVER_ERROR, message='Something Went Wrong')
            return Response(api_response)


    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        api_response = responsegenerator(status=status.HTTP_200_OK,results=serializer.data)
        return Response(api_response)


    def list(self, request, *args, **kwargs):
        # print(request.user, "*"*50)
        course = self.request.query_params.get('course')
        keyword = self.request.query_params.get('keyword')
        if keyword:
            queryset = Course.objects.filter(keyword__icontains=keyword)
        elif course:
            queryset = Course.objects.filter(title__icontains=course)
        else:
            queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            api_response = responsegenerator(status=status.HTTP_200_OK, results=serializer.data)
            return self.get_paginated_response(api_response)
        serializer = self.get_serializer(queryset, many=True)
        api_response = responsegenerator(status=status.HTTP_200_OK, results=serializer.data)
        return Response(api_response)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            self.perform_update(serializer)
            api_response = responsegenerator(status=status.HTTP_200_OK, results=serializer.data,message="Updated Successfully")
            return Response(api_response)
        api_response = responsegenerator(status=status.HTTP_400_BAD_REQUEST, errors=serializer.errors)
        return Response(api_response)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        api_response = responsegenerator(status=status.HTTP_204_NO_CONTENT, message="Deleted Successfully.")
        return Response(api_response)



class ModuleViewSet(viewsets.ModelViewSet):
    queryset = Module.objects.all()
    serializer_class = ModuleSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    def create(self, request, *args, **kwargs):
        try:
            data = request.data
            course_id = data.get('course')

            # Checking if the user is the creator of the course
            if request.user != Course.objects.get(id=course_id).creator:
                api_response = responsegenerator(status=status.HTTP_401_UNAUTHORIZED, message="You do not have permission to add modules to this course.")
                return Response(api_response, status=status.HTTP_401_UNAUTHORIZED)
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                api_response = responsegenerator(status=status.HTTP_201_CREATED, results=serializer.data, message="Module added successfully.")
                return Response(api_response, status=status.HTTP_201_CREATED)
            api_response = responsegenerator(status=status.HTTP_400_BAD_REQUEST, errors=serializer.errors)
            return Response(api_response, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(e)
            api_response = responsegenerator(status=status.HTTP_500_INTERNAL_SERVER_ERROR, message='Something went wrong')
            return Response(api_response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        api_response = responsegenerator(status=status.HTTP_200_OK, results=serializer.data)
        return Response(api_response, status=status.HTTP_200_OK)

    def list(self, request, *args, **kwargs):
        course_id = self.request.query_params.get("course_id")
        if not course_id:
            api_response = responsegenerator(status=status.HTTP_204_NO_CONTENT, message="No Course Selected")
            return Response(api_response)

        queryset = Module.objects.filter(course=int(course_id)).order_by('order')

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            api_response = responsegenerator(status=status.HTTP_200_OK, results=serializer.data)
            return self.get_paginated_response(api_response)
        serializer = self.get_serializer(queryset, many=True)
        api_response = responsegenerator(status=status.HTTP_200_OK, results=serializer.data)
        return Response(api_response, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            self.perform_update(serializer)
            api_response = responsegenerator(status=status.HTTP_200_OK, results=serializer.data, message="Module updated successfully.")
            return Response(api_response, status=status.HTTP_200_OK)
        api_response = responsegenerator(status=status.HTTP_400_BAD_REQUEST, errors=serializer.errors)
        return Response(api_response, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        api_response = responsegenerator(status=status.HTTP_204_NO_CONTENT, message="Module deleted successfully.")
        return Response(api_response, status=status.HTTP_204_NO_CONTENT)
    

class ContentViewset(viewsets.ModelViewSet):
    queryset = Content.objects.all()
    serializer_class = ContentSerializer
    permission_classes = [IsAuthenticated, IsModuleOwnerOrReadOnly]

    def create(self, request, *args, **kwargs):
        try:
            data = request.data
            module_id = data.get('module')
            module = Module.objects.get(id=module_id)
            if module.course.creator != request.user:
                api_response = responsegenerator(status=status.HTTP_401_UNAUTHORIZED, message="You do not have permission to add content to this module.")
                return Response(api_response)
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                api_response = responsegenerator(status=status.HTTP_201_CREATED, results=serializer.data, message="Content added successfully.")
                return Response(api_response)
            api_response = responsegenerator(status=status.HTTP_400_BAD_REQUEST, errors=serializer.errors)
            return Response(api_response)
        except Exception as e:
            print(e)
            api_response = responsegenerator(status=status.HTTP_500_INTERNAL_SERVER_ERROR, message='Something went wrong.')
            return Response(api_response)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        api_response = responsegenerator(status=status.HTTP_200_OK, results=serializer.data)
        return Response(api_response)

    def list(self, request, *args, **kwargs):
        # queryset = self.filter_queryset(self.get_queryset())
        module_id = self.request.query_params.get("module_id")
        if not module_id:
            api_response = responsegenerator(status=status.HTTP_204_NO_CONTENT, message="No Module Selected")
            return Response(api_response)
        queryset = Content.objects.filter(module=int(module_id))
        serializer = self.get_serializer(queryset, many=True)
        api_response = responsegenerator(status=status.HTTP_200_OK, results=serializer.data)
        return Response(api_response)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            api_response = responsegenerator(status=status.HTTP_200_OK, results=serializer.data, message="Content updated successfully.")
            return Response(api_response)
        api_response = responsegenerator(status=status.HTTP_400_BAD_REQUEST, errors=serializer.errors)
        return Response(api_response)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        api_response = responsegenerator(status=status.HTTP_204_NO_CONTENT, message="Content deleted successfully.")
        return Response(api_response)
    

client = razorpay.Client(auth=("rzp_test_5uFkpY7sQJWElt", "eNZWVPYdNAvzHQFKIZr2kPJF"))
from rest_framework_simplejwt.authentication import JWTAuthentication

@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
@api_view(['POST'])
def createOrder(request):
    global client
    
    data = request.data
    user = int(data.get('user'))
    course = int(data.get('course'))
    total_amount = data.get('total_amount')
    amount_paid = int(float(data.get('amount_paid')))
    user = User.objects.get(id = int(user))
    if request.user != user:
        api_response = responsegenerator(status=status.HTTP_401_UNAUTHORIZED, message='You do not have permission')
        return Response(api_response)
    course = Course.objects.get(id=int(course))
    new_data = {"amount":amount_paid, "currency":"INR"}
    try:
        transaction_check = Enrollment.objects.filter(course=course,student=user)
        if len(transaction_check)>= 1:
            api_response = responsegenerator(status=status.HTTP_400_BAD_REQUEST, message="You have already purchased the course.")
            return Response(api_response)
    except Exception as e:
        print(e)
        pass

    payment = client.order.create(data=new_data)
    RazorpayOrder.objects.create(
        student=user,
        course = course,
        amount_paid = payment['amount']/100,
        total_amount = total_amount/100,
        currency = payment['currency'],
        order_id = payment['id'], 
    )
    newrazor = RazorpayOrder.objects.get(order_id=payment['id'])
    api_response = responsegenerator(status=status.HTTP_200_OK,results={'order_id': payment['id'], 'amount': payment['amount'], 'currency':payment['currency']})
    return Response(api_response)


@api_view(['POST'])
def verifySignature(request):
    global client
    data = request.data
    print(data)
    params_dict = {
        'razorpay_payment_id' : data['payment_id'],
        'razorpay_order_id' : data['order_id'],
        'razorpay_signature' : data['signature'],
        'amount':data['amount']
    }

    # verifying the signature
    res = client.utility.verify_payment_signature(params_dict)
    if res == True:
        order = RazorpayOrder.objects.get(order_id = request.data['order_id'])
        Enrollment.objects.create(
            student = order.student,
            course = order.course,
            transaction_type = 'online', 
            amount_paid = order.amount_paid, 
            total_amount = order.total_amount, 
            razorpay_id = order,
        )
        api_response = responsegenerator(status=status.HTTP_201_CREATED,message='Payment Successful')
        return Response(api_response)
    api_response = responsegenerator(status=status.HTTP_400_BAD_REQUEST,message='Payment Failed')
    return Response(api_response)

@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
@api_view(['GET'])
def getTransactionDetails(request):
    data = request.data
    user_id = request.query_params.get('user')
    user = User.objects.get(id=int(user_id))
    if request.user != user:
        api_response = responsegenerator(status=status.HTTP_401_UNAUTHORIZED, message='You do not have permission')
        return Response(api_response)
    queryset = Enrollment.objects.filter(student=int(user_id))
    serializer = EnrollmentListSerializer(queryset,many=True)
    api_response = responsegenerator(status=status.HTTP_200_OK,results=serializer.data)
    return Response(api_response)

import pyrebase

firebaseConfig = {
    "apiKey": "AIzaSyBm3--ubPJARyUzEGmwUVqqmiGeLBQbATU",
    "authDomain": "curiocamp-b13dc.firebaseapp.com",
    "databaseURL": "https://curiocamp-b13dc-default-rtdb.firebaseio.com",
    "projectId": "curiocamp-b13dc",
    "storageBucket": "curiocamp-b13dc.appspot.com",
    "messagingSenderId": "346127704571",
    "appId": "1:346127704571:web:4c77347a938eb9481e2b5e",
    "measurementId": "G-1PYWZ9RYPH"
};

firebase = pyrebase.initialize_app(firebaseConfig)
authe = firebase.auth()
database = firebase.database()

@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
@api_view(['POST'])
def postquestionfirebase(request):
    # channel_name = database.child('Data').child('Name').get().val()
    pass
from rest_framework.generics import ListCreateAPIView, CreateAPIView
from . services import AdminService
from . serializers import AdminCreateSerializer, AdminSerializer, GoogleSerializer,UserEditSerializer
from django.contrib.auth.hashers import make_password,check_password
from . utils import *
from . models import User
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.shortcuts import get_object_or_404

class AdminCreateView(CreateAPIView):
    queryset = AdminService.get_all_admins()
    serializer_class = AdminCreateSerializer
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        request.data['password'] = make_password(request.data['password'])
        serializer=self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            admin = AdminService.get_admin(serializer.data['id'])
            admin.admin_id=admin
            admin.designation='admin'
            admin.is_admin=True
            admin.save()
            admin_data=AdminSerializer(admin).data
            admin_token=create_admin_token(admin)
            return Response({"access_token":f"{admin_token['access_token']}","refresh_token":f"{admin_token['refresh_token']}","data":admin_data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AdminLoginView(CreateAPIView):
    queryset = AdminService.get_all_admins()
    serializer_class = AdminSerializer
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request, *args, **kwargs):
        admin = AdminService.get_admin_by_email(request.data['email'])
        admin_data = AdminSerializer(admin).data
        if check_password(request.data['password'], admin.password):
            admin_token=create_admin_token(admin)
            return Response({"access_token":f"{admin_token['access_token']}","refresh_token":f"{admin_token['refresh_token']}","data":admin_data}, status=status.HTTP_200_OK)
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)

class GoogleOauthView(CreateAPIView):
    queryset = AdminService.get_all_admins()
    serializer_class = AdminSerializer
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request, *args, **kwargs):
        auth_code = request.data.get('code')
        response = exchange_google_token(auth_code)
        if response.status_code != 200:
            return Response({'message': 'Unable to exchange token.', 'error': response.json()}, status=status.HTTP_400_BAD_REQUEST)
        token_info = response.json()
        id_token = token_info.get('id_token')
        google_access_token = token_info.get('access_token')
        google_refresh_token = token_info.get('refresh_token')
        decoded_token = parse_google_id_token(id_token)
        email = decoded_token.get('email')
        try:
            admin = AdminService.get_admin_by_email(email)
            admin_data = AdminSerializer(admin).data
        except User.DoesNotExist:
            return JsonResponse({'message': 'Unauthorized User'}, status=200)
        jwt_access_token, jwt_refresh_token = create_jwt_tokens(admin, google_access_token, google_refresh_token)
        return JsonResponse({'access_token': f"Bearer {jwt_access_token}", 'refresh_token': f"Bearer {jwt_refresh_token}", 'data': admin_data},status=200) 
    

from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from . services import UserService
from . serializers import UserSerializer,UserCreateSerializer
from admins.utils import decode_access_token
from rest_framework.response import Response
from rest_framework import status
from admins.services import AdminService
from django.contrib.auth.hashers import make_password,check_password

class UserListCreateView(ListCreateAPIView):
    queryset = UserService.get_all_users()

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return UserCreateSerializer
        return UserSerializer
    
    def post(self, request, *args, **kwargs):
        try:
            auth_header = request.headers.get('Authorization')
            token = auth_header.split(' ')[1]
            admin_id = decode_access_token(token).get('user_id')
            admin_obj = AdminService.get_admin(admin_id)
            request.data['admin_id'] = admin_obj.id
            request.data['password'] = make_password('testtest')
            serializer = self.get_serializer(data=request.data)
            print(serializer)
            if serializer.is_valid():
                serializer.save()
                data = serializer.data
                data.pop('admin_id')
                data.pop('password')
                return Response(data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            # Log the exception
            print(f"Exception occurred: {e}")
            # Return the exception message as a string
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    def get(self, request, *args, **kwargs):
        try:
            auth_header = request.headers.get('Authorization')
            token = auth_header.split(' ')[1]
            admin_id = decode_access_token(token).get('user_id')
            user_list=UserService.filter_user_by_admin_id(admin_id)
            serializer=UserSerializer(user_list,many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': e}, status=status.HTTP_400_BAD_REQUEST)
        
class UserRetrieveUpdateDeleteView(RetrieveUpdateDestroyAPIView):
    queryset = UserService.get_all_users()
    lookup_field = 'pk'
    http_method_names = ['put', 'delete']

    def get_serializer_class(self): 
        if self.request.method == 'PUT':
            return UserEditSerializer
        return UserSerializer
    
from rest_framework.generics import ListCreateAPIView, CreateAPIView, RetrieveUpdateDestroyAPIView
from .services import AdminService, UserService
from .serializers import AdminCreateSerializer, AdminSerializer, GoogleSerializer, UserEditSerializer, UserSerializer, UserCreateSerializer
from django.contrib.auth.hashers import make_password, check_password
from .utils import *
from .models import User
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from admins.utils import decode_access_token
from admins.services import AdminService
from projects.services import ProjectService
from projects.serializers import ProjectSerializer

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
        if admin.is_admin==False and request.data['login_type'] == 'admin':
            return Response({'error': 'Not an admin'}, status=status.HTTP_400_BAD_REQUEST)
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
            return JsonResponse({'message': 'Unauthorized User'}, status=400)
        jwt_access_token, jwt_refresh_token = create_jwt_tokens(admin, google_access_token, google_refresh_token)
        return JsonResponse({'access_token': f"Bearer {jwt_access_token}", 'refresh_token': f"Bearer {jwt_refresh_token}", 'data': admin_data},status=200) 


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
    http_method_names = ['get','put', 'delete']

    def get_serializer_class(self): 
        if self.request.method == 'PUT':
            return UserEditSerializer
        return UserSerializer
    
    def get(self, request, *args, **kwargs):
        id=kwargs['pk']
        user = UserService.get_user(id)
        user_data = UserSerializer(user).data
        projects = ProjectSerializer(ProjectService.filter_project_by_user_id(id), many=True).data
        user_data['projects'] = projects
        return Response(user_data, status=status.HTTP_200_OK)
    
    def delete(self, request, *args, **kwargs):
        id=kwargs['pk']
        user = UserService.get_user(id)
        if user.is_admin:
            return Response({'error': 'You are not authorized to delete this user'}, status=status.HTTP_400_BAD_REQUEST)
        return super().delete(request, *args, **kwargs)

class GoogleOauthSignupView(CreateAPIView):
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
        google_access_token = token_info.get('access_token')
        google_refresh_token = token_info.get('refresh_token')
        data=fetch_google_profile(google_access_token)

        user_data={
            'first_name':data['name'].split()[0],
            'last_name':data['name'].split()[1],
            'email':data['email'],
            'password':None,
            'admin_id':None,
            'designation':'admin',
            'is_admin':True
        }
        user = UserService.create_user(user_data)
        user.admin_id=user
        user.save()

        user_data = UserSerializer(user).data

        jwt_access_token, jwt_refresh_token = create_jwt_tokens(user, google_access_token, google_refresh_token)
        return JsonResponse({'access_token': f"Bearer {jwt_access_token}", 'refresh_token': f"Bearer {jwt_refresh_token}", 'data': user_data},status=200) 

class UserDataView(ListCreateAPIView):
    queryset = UserService.get_all_users()
    lookup_field = 'pk'
    http_method_names = ['get']
    serializer_class = UserSerializer
    
    def get(self, request, *args, **kwargs):
        auth_header = request.headers.get('Authorization')
        token = auth_header.split(' ')[1]
        user_id = decode_access_token(token).get('user_id')
        user = UserService.get_user(user_id)
        user_data = UserSerializer(user).data
        projects = ProjectSerializer(ProjectService.filter_project_by_user_id(user_id), many=True).data
        user_data['projects'] = projects
        return Response(user_data, status=status.HTTP_200_OK)
from rest_framework.generics import ListCreateAPIView, CreateAPIView
from . services import AdminService
from . serializers import AdminCreateSerializer, AdminSerializer, GoogleSerializer
from django.contrib.auth.hashers import make_password,check_password
from . utils import *
from . models import Admin
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

class AdminGoogleOauthView(CreateAPIView):
    queryset = AdminService.get_all_admins()
    serializer_class = GoogleSerializer
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
        except Admin.DoesNotExist:
            return JsonResponse({'message': 'Unauthorized User'}, status=200)
        jwt_access_token, jwt_refresh_token = create_jwt_tokens(admin, google_access_token, google_refresh_token)
        return JsonResponse({'access_token': f"Bearer {jwt_access_token}", 'refresh_token': f"Bearer {jwt_refresh_token}", 'data': admin_data},status=200) 
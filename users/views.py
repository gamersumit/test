from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from . services import UserService
from . serializers import UserSerializer,UserCreateSerializer
from admins.utils import decode_access_token
from rest_framework.response import Response
from rest_framework import status
from admins.services import AdminService

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
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                data=serializer.data
                data.pop('admin_id')
                return Response(data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': e}, status=status.HTTP_400_BAD_REQUEST)
    
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
            return UserCreateSerializer
        return UserSerializer

    def put(self, request, *args, **kwargs):
        auth_header = request.headers.get('Authorization')
        token = auth_header.split(' ')[1]
        admin_id = decode_access_token(token).get('user_id')
        request.data['admin_id'] = admin_id
        data=super().put(request, *args, **kwargs)
        data.data.pop('admin_id')
        return data

    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)






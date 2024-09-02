from django.shortcuts import render

# Create your views here.
from admins.utils import decode_access_token
from admins.services import AdminService
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from .services import ProjectService
from .serializers import ProjectSerializer, ProjectCreateSerializer
from rest_framework.response import Response
from rest_framework import status

class ProjectListCreateView(ListCreateAPIView):
    queryset = ProjectService.get_all_projects()
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ProjectCreateSerializer
        return ProjectSerializer

    def post(self, request, *args, **kwargs):
        auth_header = request.headers.get('Authorization')
        token = auth_header.split(' ')[1]
        admin_id = decode_access_token(token).get('user_id')
        request.data['admin_id'] = admin_id
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            project_data=ProjectSerializer(serializer.instance).data
            return Response(project_data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def get(self, request, *args, **kwargs):
        project_list = ProjectService.get_all_projects()
        serializer = ProjectSerializer(project_list, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class ProjectRetrieveUpdateDeleteView(RetrieveUpdateDestroyAPIView):
    queryset = ProjectService.get_all_projects()
    lookup_field = 'pk'
    http_method_names = ['put', 'delete']
    
    def get_serializer_class(self):
        if self.request.method == 'PUT':
            return ProjectCreateSerializer
        return ProjectSerializer

    def put(self, request, *args, **kwargs):
        auth_header = request.headers.get('Authorization')
        token = auth_header.split(' ')[1]
        admin_id = decode_access_token(token).get('user_id')
        request.data['admin_id'] = admin_id
        super().put(request, *args, **kwargs)
        project_obj = ProjectService.get_project(kwargs['pk'])
        project_data = ProjectSerializer(project_obj).data
        return Response(project_data, status=status.HTTP_200_OK)
    
    def delete(self, request, *args, **kwargs):
        auth_header = request.headers.get('Authorization')
        token = auth_header.split(' ')[1]
        admin_id = decode_access_token(token).get('user_id')
        project = ProjectService.get_project(kwargs['pk'])
        print(project.admin_id.id)
        if str(project.admin_id.id) == str(admin_id):
            return super().delete(request, *args, **kwargs)
        return Response({'error': 'You are not authorized to delete this project'}, status=status.HTTP_400_BAD_REQUEST)

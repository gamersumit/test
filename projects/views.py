from django.shortcuts import render

# Create your views here.
from admins.utils import decode_access_token
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView, CreateAPIView, DestroyAPIView
from .services import *
from .serializers import *
from rest_framework.response import Response
from rest_framework import status
import cloudinary.uploader
from admins.services import UserService

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
        if request.query_params.get('user_id'):
            project_list = ProjectService.filter_project_by_user_id(request.query_params.get('user_id'))
            serializer = ProjectSerializer(project_list, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
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

class ProjectLogsView(ListCreateAPIView):
    queryset = ProjectService.get_all_projects()
    serializer_class=LogCreateSerializer

    def get(self, request, *args, **kwargs):
        project = ProjectService.get_project(request.query_params.get('project_id'))
        logs = LogService.filter_logs_by_project_id(project.id)
        serializer = LogSerializer(logs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class ProjectLogsDetailView(RetrieveUpdateDestroyAPIView):
    queryset = LogService.get_all_logs()
    lookup_field = 'pk'
    http_method_names = ['put', 'delete']
    
    def get_serializer_class(self):
        if self.request.method == 'PUT':
            return LogCreateSerializer
        return LogSerializer

class ProjectScreenCaptureView(CreateAPIView):
    queryset = ScreenCaptureService.get_all_screen_captures()
    serializer_class=ScreenCaptureCreateSerializer
    
    def post(self, request, *args, **kwargs):
        auth_header = request.headers.get('Authorization')
        token = auth_header.split(' ')[1]
        user_id = decode_access_token(token).get('user_id')
        log = LogService.get_log(request.data.get('log_id'))
        if str(log.user_id.id) == str(user_id):
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                log.images.add(serializer.instance)
                image_data = ScreenCaptureService.get_screen_capture(serializer.instance.id)
                screen_capture_data = ScreenCaptureCreateSerializer(image_data).data
                return Response(screen_capture_data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({'error': 'You are not authorized to add screen capture to this log'}, status=status.HTTP_400_BAD_REQUEST)

class ProjectScreenCaptureDetailView(DestroyAPIView):
    queryset = ScreenCaptureService.get_all_screen_captures()
    serializer_class=ScreenCaptureCreateSerializer

    def delete(self, request, *args, **kwargs):
        auth_header = request.headers.get('Authorization')
        token = auth_header.split(' ')[1]
        user_id = decode_access_token(token).get('user_id')
        screen_capture = ScreenCaptureService.get_screen_capture(kwargs['pk'])
        log = LogService.get_log(screen_capture.log_id.id)
        if str(log.user_id.id) == str(user_id):
            image_url = screen_capture.image.url
            public_id = image_url.replace("https://res.cloudinary.com/dmxsvedfi/image/upload/v1/", "").split('.')[0]
            print(public_id)
            cloudinary.uploader.destroy(public_id)
            log.images.remove(screen_capture)
            return super().delete(request, *args, **kwargs)
        return Response({'error': 'You are not authorized to delete this screen capture'}, status=status.HTTP_400_BAD_REQUEST)
from django.shortcuts import render
import base64
from django.core.files.base import ContentFile
# Create your views here.
from admins.utils import decode_access_token
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView, CreateAPIView, DestroyAPIView, ListAPIView
from .services import *
from .serializers import *
from .utils import *
from rest_framework.response import Response
from rest_framework import status
import cloudinary.uploader
from admins.services import UserService
from datetime import datetime, time

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
        auth_header = request.headers.get('Authorization')
        token = auth_header.split(' ')[1]
        user_id = decode_access_token(token).get('user_id')
        project_list = ProjectService.filter_project_by_admin_id(user_id)
        serializer = ProjectSerializer(project_list, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class UserProjectAPIView(ListAPIView):
    serializer_class=UserProjectSerializer
    queryset = ProjectService.get_all_projects()

    def get(self, request, *args, **kwargs):
        auth_header = request.headers.get('Authorization')
        token = auth_header.split(' ')[1]
        user_id = decode_access_token(token).get('user_id')
        project_list = ProjectService.filter_project_by_user_id(user_id)
        serializer = UserProjectSerializer(project_list, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class ProjectRetrieveUpdateDeleteView(RetrieveUpdateDestroyAPIView):
    queryset = ProjectService.get_all_projects()
    lookup_field = 'pk'
    http_method_names = ['put', 'delete', 'get']
    
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
    
    def get(self, request, *args, **kwargs):
        project = ProjectService.get_project(kwargs['pk'])
        project_data = ProjectSerializer(project).data
        return Response(project_data, status=status.HTTP_200_OK)

class ProjectLogsView(ListCreateAPIView):
    queryset = ProjectService.get_all_projects()
    serializer_class=LogCreateSerializer

    def get(self, request, *args, **kwargs):
        auth_header = request.headers.get('Authorization')
        token = auth_header.split(' ')[1]
        if not request.query_params.get('user_id'):
            user_id = decode_access_token(token).get('user_id')
        else:
            user_id = request.query_params.get('user_id')
        logs = LogService.filter_logs_by_project_id_and_user_id(request.query_params.get('project_id'),user_id)
        serializer = LogSerializer(logs, many=True)
        filtered_logs = []
        for log in serializer.data:
            log['date'], log['start_time'] = convert_timestamp_iso8601(str(log['start_timestamp']),int(request.query_params.get('offset')))
            if log['end_timestamp']:
                log['end_time'] = convert_timestamp_iso8601(log['end_timestamp'],int(request.query_params.get('offset')))[1]
                filtered_logs.append(log)
        return Response(filtered_logs, status=status.HTTP_200_OK)
    
    def post(self, request, *args, **kwargs):
        auth_header = request.headers.get('Authorization')
        token = auth_header.split(' ')[1]
        user_id = decode_access_token(token).get('user_id')
        request.data['user_id'] = user_id
        serializer=self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            log_data = LogSerializer(serializer.instance).data
            log_data['date'], log_data['start_time'] = convert_timestamp_iso8601(log_data['start_timestamp'],request.data.get('offset'))
            if log_data['end_timestamp']:
                log_data['end_time'] = convert_timestamp_iso8601(log_data['end_timestamp'],request.data.get('offset'))[1]
            else:
                log_data['end_time'] = None
            return Response(log_data, status=status.HTTP_201_CREATED)
        return super().post(request, *args, **kwargs)
    
class ProjectLogsDetailView(RetrieveUpdateDestroyAPIView): 
    queryset = LogService.get_all_logs()
    lookup_field = 'pk'
    http_method_names = ['put', 'delete']
    
    def get_serializer_class(self):
        if self.request.method == 'PUT':
            return LogEditSerializer
        return LogSerializer
    
    def put(self, request, *args, **kwargs):
        auth_header = request.headers.get('Authorization')
        token = auth_header.split(' ')[1]
        user_id = decode_access_token(token).get('user_id')
        log = LogService.get_log(kwargs['pk'])
        if str(log.user_id.id) == str(user_id):
            data=super().put(request, *args, **kwargs)
            log_data = LogSerializer(LogService.get_log(kwargs['pk'])).data
            log_data['date'], log_data['start_time'] = convert_timestamp_iso8601(log_data['start_timestamp'],request.data.get('offset'))
            if log_data['end_timestamp']:
                log_data['end_time'] = convert_timestamp_iso8601(log_data['end_timestamp'],request.data.get('offset'))[1]
            else:
                log_data['end_time'] = None
            return Response(log_data, status=status.HTTP_200_OK)
        return Response({'error': 'You are not authorized to edit this log'}, status=status.HTTP_400_BAD_REQUEST)


class ProjectScreenCaptureView(CreateAPIView):
    queryset = ScreenCaptureService.get_all_screen_captures()
    serializer_class = ScreenCaptureCreateSerializer
    
    def post(self, request, *args, **kwargs):
        auth_header = request.headers.get('Authorization')
        token = auth_header.split(' ')[1]
        user_id = decode_access_token(token).get('user_id')
        log = LogService.get_log(request.data.get('log_id'))
        
        if str(log.user_id.id) == str(user_id):
            images = request.data.get('images')
            if not images:
                return Response({'error': 'No images provided'}, status=status.HTTP_400_BAD_REQUEST)
            
            saved_images = []
            for image_data in images:
                format, imgstr = image_data.split(';base64,') 
                ext = format.split('/')[-1] 
                image = ContentFile(base64.b64decode(imgstr), name=f'temp.{ext}')
                
                data = {
                    'log_id': request.data.get('log_id'),
                    'image': image
                }
                serializer = self.get_serializer(data=data)
                if serializer.is_valid():
                    serializer.save()
                    log.images.add(serializer.instance)
                    saved_images.append(ScreenCaptureCreateSerializer(serializer.instance).data)
                else:
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            return Response(saved_images, status=status.HTTP_201_CREATED)
        
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
    
class ProjectLogsFilterView(CreateAPIView):
    queryset = ProjectService.get_all_projects()
    serializer_class=LogCreateSerializer

    def post(self, request, *args, **kwargs):
        user_id = request.data.get('user_id')
        project_id = request.data.get('project_id')
        offset = int(request.data.get('offset', 0))
        date_str = request.data.get('date')  

        if not date_str:
            return Response({'error': 'Date is required'}, status=status.HTTP_400_BAD_REQUEST)

        # Parse the date
        try:
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return Response({'error': 'Invalid date format. Use YYYY-MM-DD.'}, status=status.HTTP_400_BAD_REQUEST)

        # Define the time range
        start_datetime = datetime.combine(date, time(0, 0))  # 12:00 AM
        end_datetime = datetime.combine(date, time(12, 0))   # 12:00 PM

        # Filter logs by project_id, user_id, and the specified time range
        logs = LogService.filter_logs_by_project_id_and_user_id(project_id, user_id)
        logs = logs.filter(start_timestamp__range=(start_datetime, end_datetime))

        serializer = LogSerializer(logs, many=True)
        filtered_logs = []
        for log in serializer.data:
            log['date'], log['start_time'] = convert_timestamp_iso8601(str(log['start_timestamp']), offset)
            if log['end_timestamp']:
                log['end_time'] = convert_timestamp_iso8601(log['end_timestamp'], offset)[1]
            filtered_logs.append(log)

        return Response(filtered_logs, status=status.HTTP_200_OK)
    
class ProjectsRemoveAPIView(CreateAPIView):
    queryset = ProjectService.get_all_projects()
    lookup_field = 'pk'
    
    def post(self, request, *args, **kwargs):
        projects = request.data.get('projects')
        user_id=request.data.get('user_id')

        for project in projects:
            project_data=ProjectService.get_project(project)
            project_data.users.remove(user_id)
            project_data.save()
        user = UserService.get_user(user_id)
        user_data = UserSerializer(user).data
        projects = ProjectSerializer(ProjectService.filter_project_by_user_id(user_id), many=True).data
        user_data['projects'] = projects
        return Response(user_data, status=status.HTTP_200_OK)

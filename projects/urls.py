from django.urls import path
from .views import *
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', ProjectListCreateView.as_view(), name='project-create'),
    path('logs/', ProjectLogsView.as_view(), name='log-create'),
    path('logs/screencaptures/', ProjectScreenCaptureView.as_view(), name='screencapture'),
    path('logs/screencaptures/<str:pk>/', ProjectScreenCaptureDetailView.as_view(), name='screencapture'),
    path('<str:pk>/', ProjectRetrieveUpdateDeleteView.as_view(), name='project-detail'),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
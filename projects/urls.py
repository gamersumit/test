from django.urls import path
from .views import *

urlpatterns = [
    path('', ProjectListCreateView.as_view(), name='project-create'),
    path('<str:pk>/', ProjectRetrieveUpdateDeleteView.as_view(), name='project-detail'),
]
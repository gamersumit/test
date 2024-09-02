from django.urls import path
from .views import *

urlpatterns = [
    path('', UserListCreateView.as_view(), name='user-create'),
    path('<str:pk>/', UserRetrieveUpdateDeleteView.as_view(), name='user-detail'),
]
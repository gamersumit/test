from django.urls import path
from .views import *

urlpatterns = [
    path('signup/', AdminCreateView.as_view(), name='register'),
    path('signin/', AdminLoginView.as_view(), name='login'),
    path('google/oauth/', GoogleOauthView.as_view(), name='google'),
    path('users/', UserListCreateView.as_view(), name='user-create'),
    path('users/<str:pk>/', UserRetrieveUpdateDeleteView.as_view(), name='user-detail'),
]
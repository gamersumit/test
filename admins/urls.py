from django.urls import path
from .views import *

urlpatterns = [
    path('signup/', AdminCreateView.as_view(), name='register'),
    path('signin/', AdminLoginView.as_view(), name='login'),
    path('google/oauth/', AdminGoogleOauthView.as_view(), name='google'),
]
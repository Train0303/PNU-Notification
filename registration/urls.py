from django.urls import path
from django.contrib.auth import views as auth_views

from .views import SignUpView, EmailLoginView, index


app_name = 'registration'
urlpatterns = [
    path('signup/', SignUpView.as_view(), name='signup'),
    path('login/', EmailLoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('', index, name='index'),
]
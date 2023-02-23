from django.urls import path
from django.contrib.auth import views as auth_views

from .views import SignUpView, EmailLoginView, EmailVerificationView
from .views import index, verification, check_email_duplication


app_name = 'registration'
urlpatterns = [
    path('signup/', SignUpView.as_view(), name='signup'),
    path('signup/check_email_duplication/', check_email_duplication, name="check_email_duplication"),
    path('signup/verification/', verification, name='verification'),
    path('signup/verification/<str:uidb64>/<str:token>',EmailVerificationView.as_view(), name='verification_success'),
    path('login/', EmailLoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('', index, name='index'),
]
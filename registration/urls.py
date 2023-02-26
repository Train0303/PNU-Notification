from django.urls import path
from django.contrib.auth import views as auth_views

from .views import SignUpView, LoginView, EmailVerificationResultView
from .views import index, check_email_duplication, verification
from .views import PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView


app_name = 'registration'
urlpatterns = [
    path('signup/', SignUpView.as_view(), name='signup'),
    path('signup/check_email_duplication/', check_email_duplication, name="check_email_duplication"),
    path('signup/verification/', verification, name='verification'),
    path('signup/verification/<str:uidb64>/<str:token>',EmailVerificationResultView.as_view(), name='verification_result'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('password_reset/', PasswordResetView.as_view(), name="password_reset"),
    path('password_reset_done/', PasswordResetDoneView.as_view(), name="password_reset_done"),
    path('password_reset_confirm/<uidb64>/<token>/', PasswordResetConfirmView.as_view(), name="password_reset_confirm"),
    path('password_reset_complete/', PasswordResetCompleteView.as_view(), name="password_reset_complete"),
    path('', index, name='index'),
]
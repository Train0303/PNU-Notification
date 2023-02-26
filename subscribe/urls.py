# django import
from django.urls import path

# view import
from .views import CreateSubscribeView, UpdateSubscribeView

app_name = 'subscribe'
urlpatterns = [
    path('', CreateSubscribeView.as_view(), name="create-subscribe"),
    path('update/<int:pk>', UpdateSubscribeView.as_view(), name="update-subscribe"),
]
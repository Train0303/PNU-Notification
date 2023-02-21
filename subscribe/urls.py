# django import
from django.urls import path

# view import
from .views import CreateSubscribeView

app_name = 'subscribe'
urlpatterns = [
    path('', CreateSubscribeView.as_view(), name="create-subscribe")
]
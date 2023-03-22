# django import
from django.urls import path

# view import
from .views import CreateSubscribeView, UpdateSubscribeView, UpdateSubscribeActiveView, DeleteSubscribeView
from .views import UpdateHakjisiSubscribeActiveView, UpdateHakjisiSubscribeView
app_name = 'subscribe'
urlpatterns = [
    path('', CreateSubscribeView.as_view(), name="create-subscribe"),
    path('update/<int:pk>', UpdateSubscribeView.as_view(), name="update-subscribe"),
    path('update/hakjisi/<int:pk>', UpdateHakjisiSubscribeView.as_view(), name="update-hakjisi-subscribe"),
    path('update/active/<int:pk>', UpdateSubscribeActiveView.as_view(), name="update-subscribe-active"),
    path('update/active/hakjisi/<int:pk>', UpdateHakjisiSubscribeActiveView.as_view(), name="update-hakjisi-subscribe-active"),
    path('delete/<int:pk>', DeleteSubscribeView.as_view(), name="delete-subscribe"),
]
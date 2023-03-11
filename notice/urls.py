from django.urls import path
from .views import CreateNoticeView

app_name = 'notice'
urlpatterns = [
    path('', CreateNoticeView.as_view(), name='notice-create')
]
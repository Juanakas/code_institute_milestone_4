from django.urls import path

from . import views

app_name = 'videos'

urlpatterns = [
    path('', views.member_library, name='member-library'),
]

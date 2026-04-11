from django.urls import path

from . import views

app_name = 'videos'

urlpatterns = [
    path('', views.member_library, name='member-library'),
    path('video/<slug:slug>/', views.lesson_video, name='lesson-video'),
]

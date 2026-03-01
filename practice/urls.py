from django.urls import path

from . import views

app_name = 'practice'

urlpatterns = [
    path('', views.practice_log_list, name='list'),
    path('new/', views.practice_log_create, name='create'),
    path('<int:pk>/edit/', views.practice_log_edit, name='edit'),
]

from django.urls import path

from . import views

app_name = 'practice'

urlpatterns = [
	path('', views.practice_list, name='list'),
	path('new/', views.practice_create, name='create'),
	path('<int:log_id>/edit/', views.practice_edit, name='edit'),
]

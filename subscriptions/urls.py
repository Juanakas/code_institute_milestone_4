from django.urls import path

from . import views

app_name = 'subscriptions'

urlpatterns = [
    path('', views.pricing, name='pricing'),
    path('status/', views.subscription_status, name='status'),
    path('activate-free/', views.activate_free_membership, name='activate_free'),
]

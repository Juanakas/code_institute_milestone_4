from django.urls import path
from . import views

app_name = 'checkout'

urlpatterns = [
    path('create/', views.create_checkout_session, name='create_checkout_session'),
    path('dev-complete/', views.dev_complete_payment, name='dev_complete_payment'),
    path('success/', views.success, name='success'),
]

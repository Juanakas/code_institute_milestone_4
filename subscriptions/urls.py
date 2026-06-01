from django.urls import path

from . import views

app_name = 'subscriptions'

urlpatterns = [
    path('', views.pricing, name='pricing'),
    path('checkout/', views.create_checkout_session, name='checkout'),
    path('status/', views.subscription_status, name='status'),
    path('success/', views.subscription_success, name='subscription_success'),
    path('manage/', views.manage_subscription, name='manage'),
]

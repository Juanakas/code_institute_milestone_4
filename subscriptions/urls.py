from django.urls import path

from . import views

app_name = 'subscriptions'

urlpatterns = [
    path('', views.pricing, name='pricing'),
    path('status/', views.subscription_status, name='status'),
    path('activate-free/', views.activate_free_membership, name='activate_free'),
    path('checkout/<int:plan_id>/', views.create_checkout_session, name='checkout'),
    path('success/', views.checkout_success, name='checkout_success'),
    path('cancel/', views.checkout_cancel, name='checkout_cancel'),
    path('webhook/', views.stripe_webhook, name='webhook'),
]

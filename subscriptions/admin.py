from django.contrib import admin

from .models import SubscriptionPlan


@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
	list_display = ('name', 'stripe_price_id', 'monthly_price', 'is_active')
	list_filter = ('is_active',)
	search_fields = ('name', 'stripe_price_id')

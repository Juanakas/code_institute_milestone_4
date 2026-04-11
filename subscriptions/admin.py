from django.contrib import admin

from .models import SubscriptionPlan


@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
	list_display = ('name', 'monthly_price', 'is_active')
	list_filter = ('is_active',)
	search_fields = ('name',)

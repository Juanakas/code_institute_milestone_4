from django.contrib import admin

from .models import Membership, SubscriptionPlan


@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
	list_display = ('name', 'monthly_price', 'is_active')
	list_filter = ('is_active',)
	search_fields = ('name', 'stripe_price_id')


@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
	list_display = ('user', 'status', 'current_period_end', 'updated_at')
	list_filter = ('status',)
	search_fields = ('user__username', 'user__email', 'stripe_customer_id', 'stripe_subscription_id')

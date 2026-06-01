from django.contrib import admin

from .models import Membership, SubscriptionPlan


@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
	list_display = ('name', 'stripe_price_id', 'monthly_price', 'is_active')
	list_filter = ('is_active',)
	search_fields = ('name', 'stripe_price_id')


@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
	list_display = ('user', 'status', 'current_period_end', 'cancel_at_period_end')
	list_filter = ('status', 'cancel_at_period_end')
	search_fields = ('user__username', 'user__email', 'stripe_customer_id', 'stripe_subscription_id')
	readonly_fields = ('updated_at',)

from django.contrib import admin

from .models import CheckoutFeedback


@admin.register(CheckoutFeedback)
class CheckoutFeedbackAdmin(admin.ModelAdmin):
    list_display = ('user', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('user__username', 'user__email', 'comments')

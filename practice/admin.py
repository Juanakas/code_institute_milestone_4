from django.contrib import admin

from .models import PracticeLog


@admin.register(PracticeLog)
class PracticeLogAdmin(admin.ModelAdmin):
	list_display = ('user', 'video', 'practiced_on', 'minutes')
	list_filter = ('practiced_on',)
	search_fields = ('user__username', 'notes', 'video__title')

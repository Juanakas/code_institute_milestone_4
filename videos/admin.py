from django.contrib import admin

from .models import VideoLesson


@admin.register(VideoLesson)
class VideoLessonAdmin(admin.ModelAdmin):
	list_display = ('title', 'level', 'release_date', 'is_published')
	list_filter = ('level', 'is_published')
	prepopulated_fields = {'slug': ('title',)}
	search_fields = ('title', 'description')

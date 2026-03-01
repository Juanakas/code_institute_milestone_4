from django.db import models
from django.contrib.auth.models import User

from videos.models import VideoLesson


class PracticeLog(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='practice_logs')
	video = models.ForeignKey(VideoLesson, on_delete=models.SET_NULL, null=True, blank=True)
	practiced_on = models.DateField()
	minutes = models.PositiveIntegerField()
	notes = models.TextField()
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ['-practiced_on', '-created_at']

	def __str__(self):
		return f'{self.user.username} - {self.practiced_on} ({self.minutes} min)'

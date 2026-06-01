from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinLengthValidator, MinValueValidator
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

from videos.models import VideoLesson


class PracticeLog(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='practice_logs')
	video = models.ForeignKey(VideoLesson, on_delete=models.SET_NULL, null=True, blank=True)
	practiced_on = models.DateField()
	minutes = models.PositiveIntegerField(validators=[MinValueValidator(5), MaxValueValidator(600)])
	notes = models.TextField(validators=[MinLengthValidator(10)])
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ['-practiced_on', '-created_at']

	def __str__(self):
		return f'{self.user.username} - {self.practiced_on} ({self.minutes} min)'

	def clean(self):
		super().clean()
		errors = {}
		if self.practiced_on and self.practiced_on > timezone.localdate():
			errors['practiced_on'] = 'Practice date cannot be in the future.'
		if self.notes:
			self.notes = self.notes.strip()
		if errors:
			raise ValidationError(errors)

	def save(self, *args, **kwargs):
		self.full_clean()
		super().save(*args, **kwargs)

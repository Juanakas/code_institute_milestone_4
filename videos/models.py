from django.db import models
from django.utils import timezone


class VideoLesson(models.Model):
	BEGINNER = 'beginner'
	INTERMEDIATE = 'intermediate'
	ADVANCED = 'advanced'
	LEVEL_CHOICES = [
		(BEGINNER, 'Beginner'),
		(INTERMEDIATE, 'Intermediate'),
		(ADVANCED, 'Advanced'),
	]

	title = models.CharField(max_length=150)
	slug = models.SlugField(unique=True)
	description = models.TextField()
	level = models.CharField(max_length=20, choices=LEVEL_CHOICES, default=BEGINNER)
	video_url = models.URLField(blank=True)
	release_date = models.DateField(default=timezone.now)
	is_published = models.BooleanField(default=False)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ['-release_date', '-created_at']

	def __str__(self):
		return self.title

	@property
	def is_released(self):
		return self.is_published and self.release_date <= timezone.now().date()

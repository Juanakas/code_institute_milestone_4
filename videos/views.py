from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils import timezone

from subscriptions.decorators import subscription_required

from .models import VideoLesson


@login_required
@subscription_required
def member_library(request):
	selected_level = request.GET.get('level', '')
	lessons = VideoLesson.objects.filter(
		is_published=True,
		release_date__lte=timezone.now().date(),
	)
	if selected_level:
		lessons = lessons.filter(level=selected_level)

	context = {
		'lessons': lessons,
		'selected_level': selected_level,
		'levels': VideoLesson.LEVEL_CHOICES,
	}
	return render(request, 'videos/member_library.html', context)

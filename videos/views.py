from datetime import date
from pathlib import Path

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import FileResponse, Http404
from django.urls import reverse
from django.templatetags.static import static
from django.shortcuts import render
from django.utils import timezone

from subscriptions.decorators import subscription_required

from .models import VideoLesson


VIDEO_LIBRARY = [
	{
		'slug': 'beginner-partnerwork-combination-1',
		'title': 'Bachata Basics: Frame and Connection for Partnerwork Combination #1',
		'description': 'Beginner-friendly partnerwork focused on frame, connection, and clear lead-and-follow basics.',
		'level': VideoLesson.BEGINNER,
		'release_date': date(2025, 8, 19),
		'filename': '20250819_beginner.mp4',
		'poster': 'images/video-posters/20250819_beginner.svg',
		'captions': 'vtt/20250819_beginner.vtt',
		'duration': '12 min',
		'chapters': [
			{'time': 0, 'label': 'Welcome and frame reset'},
			{'time': 95, 'label': 'Connection and posture drill'},
			{'time': 305, 'label': 'Combination walk-through'},
			{'time': 535, 'label': 'Repeat with musical counts'},
		],
		'takeaways': [
			'Learn how to keep connection light and clear.',
			'Use the counts to stay steady through the partnerwork.',
		],
	},
	{
		'slug': 'intermediate-partnerwork-combination-2',
		'title': 'Partner Turns and Timing Drill for Partnerwork Combination #2',
		'description': 'Intermediate practice for cleaner turns, timing control, and smoother partner transitions.',
		'level': VideoLesson.INTERMEDIATE,
		'release_date': date(2025, 10, 23),
		'filename': '20251023_intermediate.mp4',
		'poster': 'images/video-posters/20251023_intermediate.svg',
		'captions': 'vtt/20251023_intermediate.vtt',
		'duration': '14 min',
		'chapters': [
			{'time': 0, 'label': 'Timing reset and prep'},
			{'time': 120, 'label': 'Turn mechanics'},
			{'time': 350, 'label': 'Partner transitions'},
			{'time': 600, 'label': 'Timing drill with music'},
		],
		'takeaways': [
			'Keep the timing inside the count before you speed up.',
			'Use the drill to find a smoother lead into the turn.',
		],
	},
	{
		'slug': 'advanced-partnerwork-combination-3',
		'title': 'Musicality and Styling Flow for Partnerwork Combination #3',
		'description': 'Advanced partnerwork that adds musicality, styling, and flow through the combination.',
		'level': VideoLesson.ADVANCED,
		'release_date': date(2025, 11, 8),
		'filename': '20251108_advanced.mp4',
		'poster': 'images/video-posters/20251108_advanced.svg',
		'captions': 'vtt/20251108_advanced.vtt',
		'duration': '16 min',
		'chapters': [
			{'time': 0, 'label': 'Styling focus and frame'},
			{'time': 145, 'label': 'Musical accents'},
			{'time': 415, 'label': 'Flow and variation'},
			{'time': 690, 'label': 'Full combination with phrasing'},
		],
		'takeaways': [
			'Add styling without breaking the partnership connection.',
			'Listen for phrasing changes to shape the movement.',
		],
	},
]

VIDEO_LIBRARY_BY_SLUG = {lesson['slug']: lesson for lesson in VIDEO_LIBRARY}


def build_video_lessons(selected_level=''):
	lessons = []
	level_labels = dict(VideoLesson.LEVEL_CHOICES)
	ordered_lessons = [lesson for lesson in VIDEO_LIBRARY if not selected_level or lesson['level'] == selected_level]

	for index, lesson in enumerate(ordered_lessons):
		next_lesson = ordered_lessons[index + 1] if index + 1 < len(ordered_lessons) else None

		lessons.append({
			**lesson,
			'level_display': level_labels.get(lesson['level'], lesson['level'].title()),
			'video_url': reverse('videos:lesson-video', kwargs={'slug': lesson['slug']}),
			'poster_url': static(lesson['poster']),
			'captions_url': static(lesson['captions']),
			'is_released': lesson['release_date'] <= timezone.now().date(),
			'player_id': f'player-{lesson["slug"]}',
			'progress_id': f'progress-{lesson["slug"]}',
			'favorite_id': f'favorite-{lesson["slug"]}',
			'bookmark_id': f'bookmark-{lesson["slug"]}',
			'next_title': next_lesson['title'] if next_lesson else '',
			'next_slug': next_lesson['slug'] if next_lesson else '',
			'next_player_id': f'player-{next_lesson["slug"]}' if next_lesson else '',
			'position_label': f'{index + 1} of {len(ordered_lessons)}',
		})

	return lessons


@login_required
@subscription_required
def member_library(request):
	selected_level = request.GET.get('level', '')
	lessons = build_video_lessons(selected_level=selected_level)
	continue_start = lessons[0] if lessons else None
	featured_lesson = lessons[1] if len(lessons) > 1 else continue_start

	context = {
		'lessons': lessons,
		'selected_level': selected_level,
		'levels': VideoLesson.LEVEL_CHOICES,
		'lesson_count': len(lessons),
		'continue_start': continue_start,
		'featured_lesson': featured_lesson,
	}
	return render(request, 'videos/member_library.html', context)


@login_required
@subscription_required
def lesson_video(request, slug):
	lesson = VIDEO_LIBRARY_BY_SLUG.get(slug)
	if not lesson:
		raise Http404('Video not found')

	video_path = Path(settings.BASE_DIR) / 'videos' / lesson['filename']
	if not video_path.exists():
		raise Http404('Video file not found')

	return FileResponse(video_path.open('rb'), content_type='video/mp4')

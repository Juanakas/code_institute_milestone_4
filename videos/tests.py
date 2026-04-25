from datetime import timedelta

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from subscriptions.models import Membership
from videos.views import build_video_lessons


class MemberLibraryTests(TestCase):
	def setUp(self):
		self.user = User.objects.create_user(username='member', password='testpass123')
		self.membership = getattr(self.user, 'membership', None)
		if self.membership is None:
			self.membership = Membership.objects.create(user=self.user)

		self.membership.status = Membership.STATUS_ACTIVE
		self.membership.current_period_end = timezone.now() + timedelta(days=30)
		self.membership.save()
		self.client.force_login(self.user)

	def test_member_library_shows_embedded_lessons(self):
		response = self.client.get(reverse('videos:member-library'))

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, 'Bachata Basics: Frame and Connection for Partnerwork Combination #1')
		self.assertContains(response, 'Partner Turns and Timing Drill for Partnerwork Combination #2')
		self.assertContains(response, 'Musicality and Styling Flow for Partnerwork Combination #3')
		self.assertContains(response, '<video', html=False)
		self.assertNotContains(response, 'data-video-toggle', html=False)
		self.assertNotContains(response, 'Play lesson')
		self.assertContains(response, 'track kind="captions"', html=False)
		self.assertContains(response, 'controlslist="nodownload noplaybackrate"', html=False)

	def test_video_library_maps_new_files_to_levels(self):
		lessons = build_video_lessons()

		self.assertEqual([lesson['level'] for lesson in lessons], ['beginner', 'intermediate', 'advanced'])
		self.assertEqual([lesson['filename'] for lesson in lessons], [
			'20251023_beginner.mp4',
			'20250819_intermediate.mp4',
			'20260422_advanced.mp4',
		])

	def test_lesson_video_endpoint_serves_each_new_video(self):
		for slug in [
			'beginner-partnerwork-combination-1',
			'intermediate-partnerwork-combination-2',
			'advanced-partnerwork-combination-3',
		]:
			with self.subTest(slug=slug):
				response = self.client.get(reverse('videos:lesson-video', kwargs={'slug': slug}))

				self.assertEqual(response.status_code, 200)
				self.assertEqual(response['Content-Type'], 'video/mp4')
				self.assertIn('Content-Length', response)
				self.assertGreater(int(response['Content-Length']), 1000000)

from datetime import timedelta

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from practice.models import PracticeLog
from practice.forms import PracticeLogForm
from videos.models import VideoLesson


class PracticePageTests(TestCase):
	def setUp(self):
		self.user = User.objects.create_user(username='member', password='testpass123')
		self.membership = self.user.membership
		self.membership.status = self.membership.STATUS_ACTIVE
		self.membership.current_period_end = timezone.now() + timedelta(days=30)
		self.membership.save()
		self.video = VideoLesson.objects.create(
			title='Footwork Basics',
			slug='footwork-basics',
			description='Practice footwork timing and balance.',
			level=VideoLesson.BEGINNER,
			video_url='https://example.com/footwork-basics.mp4',
			release_date=timezone.now().date(),
			is_published=True,
		)
		self.client.force_login(self.user)

	def test_practice_list_uses_shared_heading_style(self):
		PracticeLog.objects.create(
			user=self.user,
			video=self.video,
			practiced_on=timezone.now().date(),
			minutes=30,
			notes='Worked on timing and body isolation.',
		)
		response = self.client.get(reverse('practice:list'))

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, 'Practice logs')
		self.assertContains(response, 'Track a session in one place.')
		self.assertContains(response, 'Footwork Basics')
		self.assertContains(response, 'Worked on timing and body isolation.')

	def test_practice_form_uses_shared_heading_style(self):
		response = self.client.get(reverse('practice:create'))

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, 'New log')
		self.assertContains(response, 'Keep your notes short and easy to scan.')

	def test_practice_create_saves_log(self):
		response = self.client.post(reverse('practice:create'), {
			'video': self.video.id,
			'practiced_on': timezone.now().date().isoformat(),
			'minutes': 45,
			'notes': 'A focused 45 minute session on footwork drills.',
		})

		self.assertEqual(response.status_code, 302)
		self.assertEqual(PracticeLog.objects.count(), 1)
		log = PracticeLog.objects.get()
		self.assertEqual(log.user, self.user)
		self.assertEqual(log.video, self.video)

	def test_practice_form_rejects_future_date(self):
		future_date = (timezone.now() + timedelta(days=1)).date().isoformat()
		form = PracticeLogForm(data={
			'video': self.video.id,
			'practiced_on': future_date,
			'minutes': 45,
			'notes': 'A focused 45 minute session on footwork drills.',
		})

		self.assertFalse(form.is_valid())
		self.assertIn('practiced_on', form.errors)

	def test_practice_form_rejects_short_notes(self):
		form = PracticeLogForm(data={
			'video': self.video.id,
			'practiced_on': timezone.now().date().isoformat(),
			'minutes': 45,
			'notes': 'too short',
		})

		self.assertFalse(form.is_valid())
		self.assertIn('notes', form.errors)

	def test_practice_edit_updates_log(self):
		log = PracticeLog.objects.create(
			user=self.user,
			video=self.video,
			practiced_on=timezone.now().date(),
			minutes=20,
			notes='Warm up session with basic footwork.',
		)
		response = self.client.post(reverse('practice:edit', args=[log.id]), {
			'video': self.video.id,
			'practiced_on': timezone.now().date().isoformat(),
			'minutes': 35,
			'notes': 'Updated notes with more detail for the next session.',
		})

		self.assertEqual(response.status_code, 302)
		log.refresh_from_db()
		self.assertEqual(log.minutes, 35)
		self.assertEqual(log.notes, 'Updated notes with more detail for the next session.')

	def test_practice_delete_removes_log(self):
		log = PracticeLog.objects.create(
			user=self.user,
			video=self.video,
			practiced_on=timezone.now().date(),
			minutes=25,
			notes='Delete this log.',
		)
		response = self.client.post(reverse('practice:delete', args=[log.id]))

		self.assertEqual(response.status_code, 302)
		self.assertFalse(PracticeLog.objects.filter(id=log.id).exists())

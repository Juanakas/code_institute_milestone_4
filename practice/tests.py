from datetime import timedelta

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone


class PracticePageTests(TestCase):
	def setUp(self):
		self.user = User.objects.create_user(username='member', password='testpass123')
		self.membership = self.user.membership
		self.membership.status = self.membership.STATUS_ACTIVE
		self.membership.current_period_end = timezone.now() + timedelta(days=30)
		self.membership.save()
		self.client.force_login(self.user)

	def test_practice_list_uses_shared_heading_style(self):
		response = self.client.get(reverse('practice:list'))

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, 'Practice logs')
		self.assertContains(response, 'Track a session in one place.')

	def test_practice_form_uses_shared_heading_style(self):
		response = self.client.get(reverse('practice:create'))

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, 'New log')
		self.assertContains(response, 'Keep your notes short and easy to scan.')

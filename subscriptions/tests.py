from datetime import timedelta

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone


class SubscriptionPageTests(TestCase):
	def setUp(self):
		self.user = User.objects.create_user(username='subscriber', password='testpass123')
		self.client.force_login(self.user)

	def test_pricing_page_explains_member_area(self):
		response = self.client.get(reverse('subscriptions:pricing'))

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, 'Choose a plan.')
		self.assertContains(response, 'Member library')

	def test_status_page_shows_access_summary(self):
		membership = self.user.membership
		membership.status = membership.STATUS_ACTIVE
		membership.current_period_end = timezone.now() + timedelta(days=30)
		membership.save()

		response = self.client.get(reverse('subscriptions:status'))

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, 'Your access.')
		self.assertContains(response, 'Open Member Library')

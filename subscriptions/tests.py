from datetime import timedelta
from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from subscriptions.models import Membership, SubscriptionPlan


class SubscriptionPageTests(TestCase):
	def setUp(self):
		self.user = User.objects.create_user(username='subscriber', password='testpass123')
		SubscriptionPlan.objects.create(
			name='Members Area Subscription',
			stripe_price_id='price_test_123',
			monthly_price='19.99',
			is_active=True,
		)
		self.client.force_login(self.user)

	def test_pricing_page_explains_member_area(self):
		response = self.client.get(reverse('subscriptions:pricing'))

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, 'Join the members area.')
		self.assertContains(response, 'Member library')

	def test_status_page_shows_access_summary(self):
		membership = self.user.membership
		membership.status = membership.STATUS_ACTIVE
		membership.current_period_end = timezone.now() + timedelta(days=30)
		membership.save()

		response = self.client.get(reverse('subscriptions:status'))

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, 'Your subscription.')
		self.assertContains(response, 'Open Member Library')

	@patch('subscriptions.views.stripe.checkout.Session.create')
	def test_checkout_session_redirects_to_stripe(self, mock_create):
		mock_create.return_value = type('Session', (), {'url': 'https://checkout.stripe.test/session'})()
		response = self.client.post(reverse('subscriptions:checkout'))

		self.assertEqual(response.status_code, 302)
		self.assertEqual(response['Location'], 'https://checkout.stripe.test/session')

	@patch('subscriptions.webhooks.stripe.Webhook.construct_event')
	@patch('subscriptions.webhook_handler.stripe.Subscription.retrieve')
	def test_webhook_marks_membership_active(self, mock_retrieve, mock_construct_event):
		mock_construct_event.return_value = {
			'type': 'checkout.session.completed',
			'data': {
				'object': {
					'subscription': 'sub_123',
					'client_reference_id': str(self.user.id),
					'metadata': {'user_id': str(self.user.id)},
					'customer': 'cus_123',
					'customer_email': self.user.email,
				},
			},
		}
		mock_retrieve.return_value = {
			'id': 'sub_123',
			'customer': 'cus_123',
			'status': 'active',
			'cancel_at_period_end': False,
			'current_period_end': int((timezone.now() + timedelta(days=30)).timestamp()),
			'items': {'data': [{'price': {'id': 'price_123'}}]},
			'metadata': {'user_id': str(self.user.id)},
		}

		response = self.client.post(
			reverse('stripe-webhook'),
			data=b'{}',
			content_type='application/json',
			HTTP_STRIPE_SIGNATURE='sig',
		)

		self.assertEqual(response.status_code, 200)
		membership = Membership.objects.get(user=self.user)
		self.assertEqual(membership.status, Membership.STATUS_ACTIVE)
		self.assertEqual(membership.stripe_subscription_id, 'sub_123')

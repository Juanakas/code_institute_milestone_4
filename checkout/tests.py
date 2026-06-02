from datetime import timedelta
from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from checkout.models import CheckoutFeedback
from subscriptions.models import Membership


class CheckoutSecurityTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='payer', password='testpass123')

    def _valid_demo_payment_payload(self):
        return {
            'full_name': 'Test User',
            'email': 'payer@example.com',
            'address_line_1': '123 Main Street',
            'city': 'Dublin',
            'postal_code': 'D01AA00',
            'country': 'Ireland',
            'cardholder_name': 'Test User',
            'card_number': '4242 4242 4242 4242',
            'expiry_month': 12,
            'expiry_year': timezone.now().year + 1,
            'cvc': '123',
            'accept_terms': 'on',
        }

    @override_settings(DEBUG=True, STRIPE_SECRET_KEY='')
    def test_create_checkout_session_renders_demo_form_when_stripe_not_configured(self):
        self.client.force_login(self.user)

        response = self.client.post(reverse('checkout:create_checkout_session'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'checkout/checkout_preview.html')
        self.assertContains(response, 'Complete your subscription payment')

    @override_settings(DEBUG=False)
    def test_dev_complete_payment_redirects_in_production(self):
        self.client.force_login(self.user)

        response = self.client.post(reverse('checkout:dev_complete_payment'))

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('subscriptions:pricing'))
        membership = Membership.objects.get(user=self.user)
        self.assertFalse(membership.has_access)

    @override_settings(DEBUG=False)
    @patch('checkout.views.stripe.Subscription.retrieve')
    @patch('checkout.views.stripe.checkout.Session.retrieve')
    def test_success_with_session_id_activates_membership_in_production(self, mock_session_retrieve, mock_subscription_retrieve):
        self.client.force_login(self.user)
        mock_session_retrieve.return_value = {
            'id': 'cs_test_123',
            'mode': 'subscription',
            'payment_status': 'paid',
            'client_reference_id': str(self.user.id),
            'subscription': 'sub_test_123',
        }
        mock_subscription_retrieve.return_value = {
            'id': 'sub_test_123',
            'customer': 'cus_test_123',
            'status': Membership.STATUS_ACTIVE,
            'cancel_at_period_end': False,
            'current_period_end': int((timezone.now() + timedelta(days=30)).timestamp()),
            'items': {
                'data': [
                    {'price': {'id': 'price_test_123'}},
                ]
            },
        }

        response = self.client.get(reverse('checkout:success') + '?session_id=cs_test_123')

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('videos:member-library'))
        membership = Membership.objects.get(user=self.user)
        self.assertEqual(membership.status, Membership.STATUS_ACTIVE)
        self.assertTrue(membership.has_access)

    @override_settings(DEBUG=True)
    def test_dev_complete_payment_rejects_missing_required_fields(self):
        self.client.force_login(self.user)

        response = self.client.post(reverse('checkout:dev_complete_payment'), {})

        self.assertEqual(response.status_code, 400)
        membership = Membership.objects.get(user=self.user)
        self.assertFalse(membership.has_access)

    @override_settings(DEBUG=True)
    def test_dev_complete_payment_activates_membership_in_debug_with_valid_form(self):
        self.client.force_login(self.user)

        response = self.client.post(reverse('checkout:dev_complete_payment'), self._valid_demo_payment_payload())

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('videos:member-library'))
        membership = Membership.objects.get(user=self.user)
        self.assertEqual(membership.status, Membership.STATUS_ACTIVE)
        self.assertTrue(membership.current_period_end >= timezone.now() + timedelta(days=29))

    def test_success_feedback_submission_requires_active_membership(self):
        self.client.force_login(self.user)

        response = self.client.post(reverse('checkout:success'), {
            'rating': 4,
            'comments': 'Checkout felt clear and easy.',
        })

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('checkout:success'))
        self.assertEqual(CheckoutFeedback.objects.count(), 0)

    def test_success_feedback_submission_saves_for_active_membership(self):
        self.client.force_login(self.user)
        membership = Membership.objects.get(user=self.user)
        membership.status = Membership.STATUS_ACTIVE
        membership.current_period_end = timezone.now() + timedelta(days=30)
        membership.save()

        response = self.client.post(reverse('checkout:success'), {
            'rating': 5,
            'comments': 'The payment flow felt straightforward.',
        })

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('checkout:success'))
        self.assertEqual(CheckoutFeedback.objects.count(), 1)
        feedback = CheckoutFeedback.objects.first()
        self.assertEqual(feedback.user, self.user)
        self.assertEqual(feedback.rating, 5)

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from accounts.forms import SignUpForm


class SignUpFormTests(TestCase):
	def test_signup_form_rejects_duplicate_email(self):
		User.objects.create_user(username='existing', email='member@example.com', password='testpass123')
		form = SignUpForm(data={
			'username': 'newuser',
			'email': 'member@example.com',
			'password1': 'Strongpass123!',
			'password2': 'Strongpass123!',
		})

		self.assertFalse(form.is_valid())
		self.assertIn('email', form.errors)

	def test_signup_form_strips_and_normalizes_username_and_email(self):
		form = SignUpForm(data={
			'username': '  BachataFan  ',
			'email': '  FAN@EXAMPLE.COM  ',
			'password1': 'Strongpass123!',
			'password2': 'Strongpass123!',
		})

		self.assertTrue(form.is_valid())
		user = form.save(commit=False)
		self.assertEqual(user.username, 'BachataFan')
		self.assertEqual(user.email, 'fan@example.com')


class AuthPageAccessTests(TestCase):
	def test_signup_page_redirects_authenticated_users(self):
		user = User.objects.create_user(username='member', password='testpass123')
		self.client.force_login(user)

		response = self.client.get(reverse('signup'))

		self.assertEqual(response.status_code, 302)
		self.assertEqual(response.url, reverse('videos:member-library'))

	def test_login_page_redirects_authenticated_users(self):
		user = User.objects.create_user(username='member', password='testpass123')
		self.client.force_login(user)

		response = self.client.get(reverse('login'))

		self.assertEqual(response.status_code, 302)
		self.assertEqual(response.url, reverse('subscriptions:pricing'))

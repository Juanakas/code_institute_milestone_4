from django.contrib.auth.models import User
from django.test import TestCase

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

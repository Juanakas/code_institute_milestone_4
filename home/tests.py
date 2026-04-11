from django.test import TestCase
from django.urls import reverse


class HomePageTests(TestCase):
	def test_home_page_shows_members_area_preview(self):
		response = self.client.get(reverse('home:index'))

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, 'JUANAKAS_BACHATA')
		self.assertContains(response, 'Members-only Bachata training for dancers who want a simple path.')
		self.assertContains(response, 'Create an account now and get a 30-day free trial.')

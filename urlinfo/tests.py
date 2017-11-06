from django.test import TestCase

# Create your tests here.

from urlinfo.views import home

class HomeTestCase(TestCase):
    def setUp(self):
		pass        

    def test_final_home_view(self):
        """
        Given a URL; test all required info is being generated.
        """
        pass

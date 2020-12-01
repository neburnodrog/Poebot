from django.test import TestCase, RequestFactory
from poems.views import PoemView


# Create your tests here.
class PoemView(TestCase):
    def set_up(self):
        self.factory = RequestFactory()

    def test_poemview(self):
        response = self.factory.get("/index/poem/")

from django.test import TestCase
from django.test import RequestFactory
from . import views


# Create your tests here.
class TestVerseView(TestCase):
    def set_up(self):
        self.factory = RequestFactory()

    def test_verse_view(self):
        request = self.factory.get("/index/poem/")

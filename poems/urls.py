from django.urls import path
from . import views


app_name = 'poems'

urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    path("poem/", views.VerseView.as_view(), name="poem"),
]

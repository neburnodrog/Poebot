from django.urls import path
from . import views


app_name = 'poems'

urlpatterns = [
    path("", views.home_view, name="home"),
    path("crear/", views.CreatePoemView.as_view(), name="create_poem"),
    path("poema/", views.PoemView.as_view(), name="poem"),
    path("validate/", views.validate_rhyme, name="validate_rhyme"),
]

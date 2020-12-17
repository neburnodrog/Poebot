from django.urls import path
from . import views


app_name = 'poems'

urlpatterns = [
    path("", views.home_view, name="home"),
    path("crear/", views.CreatePoemView.as_view(), name="create_poem"),
    path("poema/", views.PoemView.as_view(), name="poem"),
    path("validate/", views.validate_rhyme, name="validate_rhyme"),
    path("change_verse/", views.change_verse, name="change_verse"),
    path("get_rhyme/", views.get_rhyme, name="get_rhyme"),
]

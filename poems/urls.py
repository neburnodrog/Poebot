from django.urls import path, include
from . import views


app_name = "poems"

urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    path("crear/", views.CreatePoemView.as_view(), name="create_poem"),
    path("poema/", views.PoemView.as_view(), name="poem"),
    path("validate/", views.validate_rhyme, name="validate_rhyme"),
    path("change_verse/", views.change_verse, name="change_verse"),
    path("accounts/", include("django.contrib.auth.urls")),
    path("accounts/register", views.RegisterView.as_view(), name="register"),
    path("accounts/profile/<int:pk>/", views.ProfileView.as_view(), name="profile"),
]

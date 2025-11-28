from django.urls import path

from . import views

app_name = "blog"
urlpatterns = [
    path("", views.index, name="index"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("article/<str:article_slug>/", views.article, name="article"),
    path("article/<str:article_slug>/edit/", views.edit, name="edit"),
    path("draft/<int:article_id>/", views.draft, name="draft"),
    path("autosave/", views.autosave, name="autosave"),
    path("images/upload/", views.upload_image, name="upload_image"),
    path("write/", views.write, name="write"),
]

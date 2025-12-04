from django.urls import path
from .views import api_views

urlpatterns = [
    path("images/upload/", api_views.upload_image, name="upload_image"),
    path("articles/autosave/", api_views.autosave, name="autosave_article"),
    path("search/articles/", api_views.search_article, name="search_article"),
    path("topics/", api_views.topics_api, name="topics_api"),
]
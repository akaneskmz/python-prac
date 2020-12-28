from django.urls import path, include

from django.contrib import admin

from steam import views

# To add a new path, first import the app:
# import blog
#
# Then add the new path:
# path('blog/', blog.urls, name="blog")
#
# Learn more here: https://docs.djangoproject.com/en/2.1/topics/http/urls/

urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    path("owned_games/", views.OwnedGamesView.as_view(), name="owned_games"),
    path("alt_image/<str:title>/", views.AltImageView.as_view(), name="alt_image"),
]

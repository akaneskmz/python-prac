from django.urls import path, include

from django.contrib import admin
from django.views.generic import RedirectView

admin.autodiscover()

# To add a new path, first import the app:
# import blog
#
# Then add the new path:
# path('blog/', blog.urls, name="blog")
#
# Learn more here: https://docs.djangoproject.com/en/2.1/topics/http/urls/

urlpatterns = [
    path("", RedirectView.as_view(url="steam/")),
    path("steam/", include('steam.urls'), name="steam"),
    path("line_bot/", include('line_bot.urls'), name="line_bot"),
    path("kindle_share/", include('kindle_share.urls'), name="kindle_share"),
    path("admin/", admin.site.urls),
]

from django.urls import path

from kindle_share import views

urlpatterns = [
    path("add", views.AddView.as_view(), name="add"),
]

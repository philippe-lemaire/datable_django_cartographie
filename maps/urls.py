from django.urls import path

from . import views

app_name = "maps"

urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    path("display_map", views.display_map, name="display_map"),
]

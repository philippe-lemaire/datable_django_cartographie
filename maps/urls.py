from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

app_name = "maps"

urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    path("display_map", views.display_map, name="display_map"),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

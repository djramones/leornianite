"""URL configuration for leornianite project."""

from django.conf import settings
from django.contrib import admin
from django.urls import path, include


admin.site.site_header = admin.site.site_title = "Leornianite admin"

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("notes.urls")),
]

if settings.DEBUG:
    urlpatterns.insert(0, path("__debug__/", include("debug_toolbar.urls")))

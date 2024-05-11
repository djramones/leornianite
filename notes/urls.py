from django.urls import path, reverse_lazy
from django.views.generic import RedirectView

from . import views


app_name = "notes"
urlpatterns = [
    path("new/", views.create_note, name="create-note"),
    path("list/", views.ListNotes.as_view(), name="list-notes"),
    path(
        "list/promoted/", views.ListPromotedNotes.as_view(), name="list-promoted-notes"
    ),
    path("random/", views.RandomNote.as_view(), name="random-note"),
    path("drill/", views.DrillNotes.as_view(), name="drill-notes"),
    path("<slug:slug>/delete/", views.DeleteNote.as_view(), name="delete-note"),
    path("<slug:slug>/", views.DetailNote.as_view(), name="detail-note"),
    path("", RedirectView.as_view(url=reverse_lazy("notes:list-notes"))),
]

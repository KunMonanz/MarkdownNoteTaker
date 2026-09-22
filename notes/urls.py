from django.urls import path

from notes.views import (
    GrammarCheckView,
    NoteListCreateView,
    NoteRetrieveUpdateDestroyView,
    RenderMarkdownView,
)

urlpatterns = [
    path("", NoteListCreateView.as_view(), name="note-create"),
    path(
        "check-grammar/",
        GrammarCheckView.as_view(),
        name="note-check-grammar",
    ),
    path(
        "<uuid:note_id>",
        NoteRetrieveUpdateDestroyView.as_view(),
        name="note-retrieve-update-destroy",
    ),
    path("render/", RenderMarkdownView.as_view(), name="note-render-markdown"),
]

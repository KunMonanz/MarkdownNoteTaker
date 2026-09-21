from django.urls import path

from notes.views import GrammarCheckView, NoteListCreateView, RenderMarkdownView

urlpatterns = [
    path("", NoteListCreateView.as_view(), name="note-create"),
    path(
        "check-grammar/",
        GrammarCheckView.as_view(),
        name="note-check-grammar",
    ),
    path("render/", RenderMarkdownView.as_view(), name="note-render-markdown"),
]

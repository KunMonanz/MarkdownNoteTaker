import language_tool_python
import markdown
from django.core.cache import cache
from rest_framework import generics, permissions, status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from notes.models import Note
from notes.serializers import NoteSerializer

_grammar_tool = None


def get_grammar_tool():
    global _grammar_tool
    if _grammar_tool is None:
        _grammar_tool = language_tool_python.LanguageTool("en-US")
    return _grammar_tool


class NoteListCreateView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = NoteSerializer
    parser_classes = [MultiPartParser, FormParser]

    def _cache_key(self):
        current_user_id = self.request.user.id
        return f"notes:{current_user_id}"

    def get_queryset(self):
        return Note.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        cache_key = self._cache_key()
        cache.delete(cache_key)
        serializer.save(user=self.request.user)

    def list(self, request, *args, **kwargs):
        cache_key = self._cache_key()
        cached_data = cache.get(cache_key)
        if cached_data is not None:
            return Response(cached_data, status=status.HTTP_200_OK)

        response = super().list(request, *args, **kwargs)
        cache.set(cache_key, response.data, 300)
        return response


class GrammarCheckView(APIView):
    def post(self, request, *args, **kwargs):
        text = request.data.get("text", "")
        if not text:
            return Response(
                {"error": "No text provided"}, status=status.HTTP_400_BAD_REQUEST
            )

        matches = get_grammar_tool().check(text)

        errors = [
            {
                "message": match.message,
                "context": match.context,
                "offset": match.offset,
                "errorLength": match.errorLength,
                "replacements": match.replacements[:3],
            }
            for match in matches
        ]

        return Response({"grammar_errors": errors}, status=status.HTTP_200_OK)


class RenderMarkdownView(APIView):
    def post(self, request, *args, **kwargs):
        markdown_text = request.data.get("markdown", "")

        html_content = markdown.markdown(markdown_text)

        return Response({"html": html_content}, status=status.HTTP_200_OK)

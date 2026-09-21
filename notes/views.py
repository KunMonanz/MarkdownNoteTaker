import language_tool_python
import markdown
from rest_framework import generics, permissions, status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from notes.models import Note
from notes.serializers import NoteSerializer


class NoteListCreateView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = NoteSerializer
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        return Note.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class GrammarCheckView(APIView):
    def post(self, request, *args, **kwargs):
        text = request.data.get("text", "")
        if not text:
            return Response(
                {"error": "No text provided"}, status=status.HTTP_400_BAD_REQUEST
            )

        tool = language_tool_python.LanguageTool("en-US")
        matches = tool.check(text)

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

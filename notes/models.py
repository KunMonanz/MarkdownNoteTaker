import os

import uuid6
from django.conf import settings
from django.db import models


def unique_note_filepath(instance, filename):
    ext = filename.split(".")[-1]
    unique_filename = f"{uuid6.uuid7()}.{ext}"
    return os.path.join("uploads/notes/", unique_filename)


class Note(models.Model):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid6.uuid7)
    title = models.CharField(max_length=255)
    content_markdown = models.TextField()
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notes"
    )
    attachment = models.FileField(upload_to=unique_note_filepath, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

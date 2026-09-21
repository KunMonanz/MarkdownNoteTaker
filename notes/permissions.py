from rest_framework.permissions import BasePermission

from notes.models import Note


class OwnerofNote(BasePermission):
    def has_object_permission(self, request, view, obj: Note):
        return obj.user_id == request.user.id

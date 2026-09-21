import uuid6
from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, AbstractUser
from django.db import models


class User(AbstractUser):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid6.uuid7)


class GrammarCheckLanguages(models.Model):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid6.uuid7)
    lanhuage_code = models.CharField(max_length=10)


class Profile(models.Model):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid6.uuid7)
    user = models.OneToOneField(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    preferred_language = models.ForeignKey(
        GrammarCheckLanguages, on_delete=models.CASCADE
    )

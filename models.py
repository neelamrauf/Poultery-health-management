import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Custom user model extending AbstractUser.

    Adds a ``role`` field (Farmer or Admin) and promotes ``email`` to a
    unique, required field.  ``created_at`` is recorded automatically on
    first save.
    """

    class Role(models.TextChoices):
        FARMER = "Farmer", "Farmer"
        ADMIN = "Admin", "Admin"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    email = models.EmailField(unique=True)

    role = models.CharField(
        max_length=10,
        choices=Role.choices,
    )

    created_at = models.DateTimeField(auto_now_add=True)

    # Keep inherited fields (username, password, …) from AbstractUser.
    # Nothing else needs overriding for this model.

    class Meta:
        verbose_name = "user"
        verbose_name_plural = "users"

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.username} ({self.role})"

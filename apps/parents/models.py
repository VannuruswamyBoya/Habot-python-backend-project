from django.db import models
from common.models import TimeStampedModel

class Parent(TimeStampedModel):
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True, db_index=True)
    phone = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return f"{self.name} ({self.email})"

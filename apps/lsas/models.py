from django.db import models
from django.contrib.postgres.fields import ArrayField
from common.models import TimeStampedModel

class LSAProfile(TimeStampedModel):
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True, db_index=True)
    skills = ArrayField(models.CharField(max_length=100), blank=True, default=list)
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.email})"


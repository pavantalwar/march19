from django.db import models
import uuid
from django.conf import settings


from authentication . models import (
    CustomUser
)

class PatientStatus(models.TextChoices):
    ACTIVE = "active", "Active"
    INACTIVE = "inactive", "Inactive"


class PatientRelation(models.TextChoices):
    SELF = "self", "Self"
    GUARDIAN = "guardian", "Guardian"
    FAMILY = "family", "Family"


class Patient(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    patient_id = models.CharField(max_length=20, unique=True)

    # 🔗 Link with CustomUser
    user = models.OneToOneField(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="patient_profile"
    )

    # 🔥 BASIC INFO
    full_name = models.CharField(max_length=50)
    mobile = models.CharField(max_length=15)
    address = models.TextField()

    # 🔥 EXTRA INFO
    medical_history = models.TextField(null=True, blank=True)
    emergency_contact = models.CharField(max_length=15, null=True, blank=True)
    emergency_contact_name = models.CharField(max_length=50, null=True, blank=True)

    status = models.CharField(
        max_length=20,
        choices=PatientStatus.choices,
        default=PatientStatus.ACTIVE
    )

    relation = models.CharField(
        max_length=20,
        choices=PatientRelation.choices,
        null=True,
        blank=True
    )
    # 🔥 COMMON FIELDS
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="patient_created_by"
    )

    class Meta:
        db_table = "patients"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.patient_id} - {self.full_name}"

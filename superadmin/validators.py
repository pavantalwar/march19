from rest_framework import serializers
from django.core.exceptions import ValidationError
import re
from django.utils.translation import gettext_lazy as _
from .models import PatientStatus, PatientRelation


# ================= EMAIL VALIDATOR =================
def email_validator(value):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, value):
        raise ValidationError("Enter valid email format")


# ================= MOBILE VALIDATOR =================
def mobile_validator(value):
    if not re.match(r'^[6-9]\d{9}$', value):
        raise ValidationError("Enter valid mobile number")


# ================= PASSWORD VALIDATOR =================
def validate_password(password):
    if len(password) < 5:
        raise ValidationError(
            _('Password must be at least 5 characters long.')
        )
    return password


# ================= PATIENT CREATE VALIDATOR =================
class PatientCreateValidator(serializers.Serializer):

    full_name = serializers.CharField(
        required=True,
        max_length=50,
        error_messages={
            "required": "Full name is required",
            "blank": "Full name cannot be blank"
        }
    )

    email = serializers.EmailField(
        required=True,
        validators=[email_validator],
        error_messages={
            "required": "Email is required",
            "blank": "Email cannot be blank",
            "invalid": "Enter valid email"
        }
    )

    password = serializers.CharField(
        required=True,
        min_length=5,
        validators=[validate_password],
        error_messages={
            "required": "Password is required",
            "blank": "Password cannot be blank",
            "min_length": "Password must be at least 5 characters"
        }
    )

    mobile = serializers.CharField(
        required=True,
        validators=[mobile_validator],
        error_messages={
            "required": "Mobile is required",
            "blank": "Mobile cannot be blank"
        }
    )

    gender = serializers.CharField(
        required=True,
        error_messages={
            "required": "Gender is required"
        }
    )

    age = serializers.IntegerField(
        required=True,
        min_value=0,
        error_messages={
            "required": "Age is required",
            "invalid": "Enter valid age",
            "min_value": "Age cannot be negative"
        }
    )

    address = serializers.CharField(
        required=True,
        error_messages={
            "required": "Address is required"
        }
    )

    relation = serializers.ChoiceField(
        choices=PatientRelation.choices,
        required=False,
        error_messages={
            "invalid_choice": "Invalid relation selected"
        }
    )

    image = serializers.ImageField(required=False)
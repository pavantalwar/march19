from rest_framework import serializers
from django.core.exceptions import ValidationError
import re
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _
from .models import UserRoles, GenderChoices


# ================= EMAIL VALIDATOR =================
def email_validator(value):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, value):
        raise ValidationError("Enter a valid email format.")


# ================= PASSWORD VALIDATOR =================
def validate_password(password):
    if len(password) < 5:
        raise ValidationError(
            _('Password must be at least 5 characters long.')
        )
    return password


# ================= MOBILE VALIDATOR =================
def mobile_validate(value):
    validator = RegexValidator(
        regex=r'^[6-9]\d{9}$',
        message="Enter valid mobile number"
    )
    validator(value)


# ================= REGISTER VALIDATOR =================
class UserRegisterValidator(serializers.Serializer):

    full_name = serializers.CharField(
        max_length=50,
        required=True,
        error_messages={
            "required": "Full name is required",
            "blank": "Full name cannot be empty"
        }
    )

    email = serializers.EmailField(
        required=True,
        validators=[email_validator],
        error_messages={
            "required": "Email is required",
            "blank": "Email cannot be empty",
            "invalid": "Enter valid email"
        }
    )

    password = serializers.CharField(
        required=True,
        min_length=5,
        validators=[validate_password],
        error_messages={
            "required": "Password is required",
            "blank": "Password cannot be empty",
            "min_length": "Password must be at least 5 characters"
        }
    )

    mobile = serializers.CharField(
        required=True,
        validators=[mobile_validate],
        error_messages={
            "required": "Mobile is required",
            "blank": "Mobile cannot be empty"
        }
    )

    role = serializers.ChoiceField(
        choices=UserRoles.choices,
        required=True,
        error_messages={
            "required": "Role is required",
            "invalid_choice": "Invalid role selected"
        }
    )

    gender = serializers.ChoiceField(
        choices=GenderChoices.choices,
        required=True,
        error_messages={
            "required": "Gender is required",
            "invalid_choice": "Invalid gender"
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

    image = serializers.ImageField(required=False)


# ================= LOGIN VALIDATOR =================
class LoginValidator(serializers.Serializer):
    email = serializers.EmailField(required=True, validators=[email_validator],error_messages={
            "required": "email is required"
        })

    password = serializers.CharField(required=True,error_messages={
            "required": "Password is required",
        })

    role = serializers.ChoiceField(
        choices=UserRoles.choices,
        required=True,
        error_messages={
            "required": "Role is required",
            "invalid_choice": "Invalid role selected"
        }
    )
#Django imports
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.backends import BaseBackend
from django.db.models import Q
from django.core.exceptions import ValidationError
from django.utils.timezone import datetime, get_current_timezone

#local imports
from authentication.models import CustomUser

class AuthBackend(BaseBackend):
    """
    Custom authentication backend for Django that supports login via email or mobile number.

    This backend allows users to authenticate using either their email address or mobile number,
    in addition to enforcing business rules such as:
    - Account activation
    - Password presence
    - Blocked user prevention
    - Last login timestamp update

    Methods:
        - authenticate(): Custom logic to authenticate the user.
        - get_user(): Returns a User object by its ID.

    Usage:
        Add this backend to your Django settings:

            AUTHENTICATION_BACKENDS = [
                'django.contrib.auth.backends.ModelBackend',
                'core.authentication.AuthBackend',  # This class
            ]
    """
    def authenticate(self, request, username=None, password=None, mpin=None ,**kwargs):
        try:
            user = CustomUser.objects.filter(Q(email=username) | Q(mobile=username)).first()

            if password:
                if not user.password or not user.check_password(password):
                    raise ValidationError("Invalid password.")
            else:
                raise ValidationError("Password must be provided.")
            if not user.is_active:
                raise ValidationError("This account is marked not active, Please contact admin.")
            user.last_login = datetime.now()
            user.save()
            return user
        except CustomUser.DoesNotExist as e:
            raise ValidationError("No User Found with the given email.")
        
    def get_user(self, user_id: int) -> AbstractBaseUser | None:
        try:
            return CustomUser.objects.get(id=user_id)
        except CustomUser.DoesNotExist as e:
            raise ValidationError("No User Found with the given email.")
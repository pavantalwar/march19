from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.utils.translation import gettext_lazy as _
from django.db import models
import uuid
from datetime import datetime
from django.conf import settings
import pytz


# ================= COMMON MODEL =================
class CommonModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    def last_updated(self):
        india_tz = pytz.timezone(settings.TIME_ZONE)
        return self.modified_at.astimezone(india_tz)

    def created_time(self):
        india_tz = pytz.timezone(settings.TIME_ZONE)
        return self.created_at.astimezone(india_tz)


# ================= USER ROLES =================
class UserRoles(models.TextChoices):
    SUPER_ADMIN = 'superadmin', _('Super Admin')
    OWNER = 'owner', _('Owner')
    CUSTOMER = 'customer', _('Customer')


# ================= USER MANAGER =================
class CustomUserManager(BaseUserManager):

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")

        email = self.normalize_email(email)

        extra_fields.setdefault("role", UserRoles.CUSTOMER)
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)

        user = self.model(email=email, **extra_fields)

        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()

        user.save(using=self._db)
        return user

    def create_owner(self, email, password=None, **extra_fields):
        extra_fields.setdefault("role", UserRoles.OWNER)
        extra_fields.setdefault("is_staff", True)
        return self.create_user(email, password, **extra_fields)

    def create_customer(self, email, password=None, **extra_fields):
        extra_fields.setdefault("role", UserRoles.CUSTOMER)
        return self.create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("role", UserRoles.SUPER_ADMIN)
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_admin", True)

        return self.create_user(email, password, **extra_fields)


# ================= CHOICES =================
class StatusChoices(models.TextChoices):
    ACTIVE = 'active', _('Active')
    INACTIVE = 'inactive', _("Inactive")


class GenderChoices(models.TextChoices):
    MALE = 'male', _('Male')
    FEMALE = 'female', _('Female')
    OTHERS = 'others', _('Others')


# ================= CUSTOM USER =================
class CustomUser(AbstractBaseUser):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    full_name = models.CharField(max_length=50, null=True, blank=True)
    email = models.EmailField(unique=True)
    mobile = models.CharField(max_length=15, null=True, blank=True)

    image = models.ImageField(upload_to='profile_images/', null=True, blank=True)

    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.ACTIVE
    )

    gender = models.CharField(
        max_length=15,
        choices=GenderChoices.choices,
        null=True,
        blank=True
    )

    date_of_birth = models.DateField(null=True, blank=True)
    age = models.PositiveIntegerField(null=True, blank=True)

    role = models.CharField(
        max_length=20,
        choices=UserRoles.choices
    )

    # Example relation (optional)
    # business = models.ForeignKey('yourapp.Business', null=True, blank=True, on_delete=models.SET_NULL)

    # ================= PERMISSIONS =================
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    is_blocked = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    last_login = models.DateTimeField(null=True, blank=True)
    login_attempt = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name', 'mobile']

    class Meta:
        db_table = 'users'
        ordering = ['-created_at']

    def __str__(self):
        return self.email or "No Email"

    def has_perm(self, perm, obj=None):
        return self.is_superuser

    def has_module_perms(self, app_label):
        return self.is_superuser

    def last_updated(self):
        return datetime.strftime(self.modified_at, "%d %b %Y %I:%M %p")

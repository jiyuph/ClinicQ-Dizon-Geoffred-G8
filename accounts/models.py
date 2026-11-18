from django.contrib.auth.models import AbstractUser, UserManager
from django.core.validators import RegexValidator
from django.db import models


class ClinicQUserManager(UserManager):
    """Makes every superuser a Receptionist, since the receptionist is the system admin."""

    def create_superuser(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault("role", User.Role.RECEPTIONIST)
        return super().create_superuser(username, email, password, **extra_fields)


phone_validator = RegexValidator(
    regex=r"^09\d{9}$",
    message="Enter a valid mobile number in the format 09XXXXXXXXX.",
)


class User(AbstractUser):
    """
    The USER table. Extends Django's built-in user, so passwords are hashed
    and login/logout/sessions all come from django.contrib.auth.
    """

    class Role(models.TextChoices):
        PATIENT = "PATIENT", "Patient"
        RECEPTIONIST = "RECEPTIONIST", "Receptionist"
        DOCTOR = "DOCTOR", "Doctor"

    # Override email so it is required and unique
    email = models.EmailField("email address", unique=True)

    role = models.CharField(max_length=20, choices=Role.choices, default=Role.PATIENT)
    contact_number = models.CharField(max_length=11, blank=True, validators=[phone_validator])
    profile_photo = models.ImageField(upload_to="profile_photos/", blank=True, null=True)

    objects = ClinicQUserManager()

    REQUIRED_FIELDS = ["email"]  # asked for by createsuperuser

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_role_display()})"

    @property
    def is_patient(self):
        return self.role == self.Role.PATIENT

    @property
    def is_receptionist(self):
        return self.role == self.Role.RECEPTIONIST

    @property
    def is_doctor(self):
        return self.role == self.Role.DOCTOR

    @property
    def dashboard_url_name(self):
        return {
            self.Role.PATIENT: "accounts:patient_dashboard",
            self.Role.RECEPTIONIST: "accounts:receptionist_dashboard",
            self.Role.DOCTOR: "accounts:doctor_dashboard",
        }[self.role]

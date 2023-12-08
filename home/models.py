import uuid

from django.db.models.deletion import PROTECT
from django.db import models
from django.core.mail import send_mail
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.base_user import AbstractBaseUser
from django.utils.translation import gettext_lazy as _

from .mixins import AbstractBaseSet, CustomUserManager
from .validators import StudentIdValidator

class User(AbstractBaseUser, PermissionsMixin):
    """
    A User model with admin-compliant permissions.
    email and password are required. Other fields are optional.
    """

    first_name = models.CharField(_("first name"), max_length=150, blank=True)
    last_name = models.CharField(_("last name"), max_length=150, blank=True)
    email = models.EmailField(_("deakin email address"), blank=False, unique=True)
    is_staff = models.BooleanField(
        _("staff status"),
        default=False,
        help_text=_("Designates whether the user can log into this admin site."),
    )
    is_active = models.BooleanField(
        _("active"),
        default=True,
        help_text=_(
            "Designates whether this user should be treated as active. "
            "Unselect this instead of deleting accounts."
        ),
    )
    created_at = models.DateTimeField(_("created_at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("updated_at"), auto_now=True)

    EMAIL_FIELD = "email"
    USERNAME_FIELD = "email"

    objects = CustomUserManager()

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")

    def clean(self):
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)

    def get_full_name(self):
        """
        Return the first_name plus the last_name, with a space in between.
        """
        full_name = "%s %s" % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        """Return the short name for the user."""
        return self.first_name

    def email_user(self, subject, message, from_email=None, **kwargs):
        """Send an email to this user."""
        send_mail(subject, message, from_email, [self.email], **kwargs)

class Project(AbstractBaseSet):

    id = models.UUIDField(default=uuid.uuid4, primary_key=True, unique=True)
    title = models.CharField(_("project title"), max_length=150, blank=True)
    
class Student(AbstractBaseSet):

    student_id_validator = StudentIdValidator()

    id = models.BigIntegerField(
        _("student_id"),
        primary_key=True,
        unique=True,
        help_text=_(
            "Required. Enter Deakin Student ID. Digits only."
        ),
        validators=[StudentIdValidator],
        error_messages={
            "unique": _("A user with that Student ID already exists."),
        },
    )
    user_id = models.OneToOneField(User, on_delete=PROTECT, related_name="users", blank=False, null=False)
    p1 = models.ForeignKey(Project, on_delete=PROTECT, related_name="p1", blank=False, null=False)
    p2 = models.ForeignKey(Project, on_delete=PROTECT, related_name="p2", blank=False, null=False)
    p3 = models.ForeignKey(Project, on_delete=PROTECT, related_name="p3", blank=False, null=False)
    allocated = models.ForeignKey(Project, on_delete=PROTECT, related_name="allocated", blank=True, null=True)
